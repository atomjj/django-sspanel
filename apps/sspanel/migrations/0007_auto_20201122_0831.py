# Generated by Django 3.1.1 on 2020-11-22 00:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sspanel", "0006_auto_20201111_0742"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="announcement",
            options={
                "ordering": ("-time",),
                "verbose_name": "系统公告",
                "verbose_name_plural": "系统公告",
            },
        ),
        migrations.AlterModelOptions(
            name="donate",
            options={
                "ordering": ("-time",),
                "verbose_name": "捐赠记录",
                "verbose_name_plural": "捐赠记录",
            },
        ),
        migrations.AlterModelOptions(
            name="emailsendlog",
            options={"verbose_name": "邮件发送记录", "verbose_name_plural": "邮件发送记录"},
        ),
        migrations.AlterModelOptions(
            name="goods",
            options={
                "ordering": ["order"],
                "verbose_name": "商品",
                "verbose_name_plural": "商品",
            },
        ),
        migrations.AlterModelOptions(
            name="invitecode",
            options={
                "ordering": ("used", "-created_at"),
                "verbose_name": "邀请码",
                "verbose_name_plural": "邀请码",
            },
        ),
        migrations.AlterModelOptions(
            name="moneycode",
            options={
                "ordering": ("isused",),
                "verbose_name": "充值码",
                "verbose_name_plural": "充值码",
            },
        ),
        migrations.AlterModelOptions(
            name="purchasehistory",
            options={
                "ordering": ("-created_at",),
                "verbose_name": "购买记录",
                "verbose_name_plural": "购买记录",
            },
        ),
        migrations.AlterModelOptions(
            name="rebaterecord",
            options={
                "ordering": ("-created_at",),
                "verbose_name": "返利记录",
                "verbose_name_plural": "返利记录",
            },
        ),
        migrations.AlterModelOptions(
            name="ticket",
            options={
                "ordering": ("-time",),
                "verbose_name": "工单",
                "verbose_name_plural": "工单",
            },
        ),
        migrations.AlterModelOptions(
            name="user",
            options={"verbose_name": "用户", "verbose_name_plural": "用户"},
        ),
        migrations.AlterModelOptions(
            name="usercheckinlog",
            options={"verbose_name": "用户签到记录", "verbose_name_plural": "用户签到记录"},
        ),
        migrations.AlterModelOptions(
            name="userorder",
            options={"verbose_name": "用户订单", "verbose_name_plural": "用户订单"},
        ),
        migrations.AlterModelOptions(
            name="userreflog",
            options={"verbose_name": "用户推荐记录", "verbose_name_plural": "用户推荐记录"},
        ),
        migrations.CreateModel(
            name="UserSubLog",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sub_type",
                    models.CharField(
                        choices=[
                            ("ss", "订阅SS"),
                            ("vless", "订阅Vless"),
                            ("trojan", "订阅Trojan"),
                            ("clash", "订阅Clash"),
                            ("clash_pro", "订阅ClashPro"),
                        ],
                        max_length=20,
                        verbose_name="订阅类型",
                    ),
                ),
                ("ip", models.CharField(max_length=128, verbose_name="IP地址")),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        db_index=True,
                        help_text="创建时间",
                        verbose_name="创建时间",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="用户",
                    ),
                ),
            ],
            options={
                "verbose_name": "用户订阅记录",
                "verbose_name_plural": "用户订阅记录",
                "ordering": ["-created_at"],
                "index_together": {("user", "created_at")},
            },
        ),
    ]
