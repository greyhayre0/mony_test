from django.db import models


class ExchangeRate(models.Model):
    usd_rate = models.DecimalField(
        max_digits=10, decimal_places=4, verbose_name="Курс USD к RUB"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время запроса"
        )

    class Meta:
        db_table = "exchange_rates"
        ordering = ["-timestamp"]
        verbose_name = "Курс валюты"
        verbose_name_plural = "Курсы валют"
        indexes = [
            models.Index(fields=["-timestamp"]),
        ]

    def __str__(self):
        return (f"USD/RUB: {self.usd_rate} at "
                f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
