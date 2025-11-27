import time
import requests
import logging
from django.http import JsonResponse
from django.core.cache import cache
from django.views.decorators.http import require_GET
from django.conf import settings
from .models import ExchangeRate

logger = logging.getLogger(__name__)


@require_GET
def get_current_usd(request):
    """
    Endpoint для получения текущего курса USD к RUB
    Возвращает текущий курс и 10 последних запросов
    """
    cache_key = "last_usd_request_time"
    last_request_time = cache.get(cache_key, 0)
    current_time = time.time()

    time_since_last_request = current_time - last_request_time
    if time_since_last_request < 10:
        remaining_time = 10 - time_since_last_request
        logger.warning(
            f"Request too frequent. Please wait {remaining_time:.1f} seconds"
        )
        return JsonResponse(
            {
                "error": f"Please wait{remaining_time:.1f} seconds between requests",
                "remaining_time": round(remaining_time, 1),
            },
            status=429,
        )

    try:
        logger.info("Fetching current USD exchange rate")
        response = requests.get(
            settings.EXCHANGE_RATE_API_URL, timeout=10
        )
        response.raise_for_status()

        data = response.json()
        usd_to_rub = data.get("rates", {}).get("RUB")

        if not usd_to_rub:
            logger.error("RUB rate not found in API response")
            return JsonResponse(
                {"error": "Exchange rate for RUB not available"}, status=503
            )

        exchange_rate = ExchangeRate.objects.create(usd_rate=usd_to_rub)
        logger.info(f"Saved exchange rate: {usd_to_rub}")

        cache.set(cache_key, current_time, 300)

        last_10_rates = ExchangeRate.objects.all()[:10].values(
            "usd_rate",
            "timestamp"
            )

        formatted_rates = []
        for rate in last_10_rates:
            formatted_rates.append(
                {
                    "usd_rate": float(rate["usd_rate"]),
                    "timestamp": rate["timestamp"].isoformat(),
                }
            )

        response_data = {
            "current_rate": float(usd_to_rub),
            "currency_pair": "USD/RUB",
            "timestamp": exchange_rate.timestamp.isoformat(),
            "last_10_requests": formatted_rates,
            "source_api": settings.EXCHANGE_RATE_API_URL,
        }

        return JsonResponse(response_data)

    except requests.exceptions.Timeout:
        logger.error("External API timeout")
        return JsonResponse({"error": "External service timeout"}, status=504)

    except requests.exceptions.RequestException as e:
        logger.error(f"External API error: {str(e)}")
        return JsonResponse(
            {"error": "Failed to fetch exchange rate from external service"},
            status=503
        )

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JsonResponse({"error": "Internal server error"}, status=500)
