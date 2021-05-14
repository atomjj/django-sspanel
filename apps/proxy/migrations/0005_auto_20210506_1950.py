# Generated by Django 3.2 on 2021-05-06 11:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("proxy", "0004_auto_20210504_1420"),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name="useronlineiplog",
            index_together=None,
        ),
        migrations.RemoveField(
            model_name="useronlineiplog",
            name="proxy_node",
        ),
        migrations.RemoveField(
            model_name="useronlineiplog",
            name="user",
        ),
        migrations.AddField(
            model_name="usertrafficlog",
            name="ip_list",
            field=models.JSONField(default=list, verbose_name="IP地址列表"),
        ),
        migrations.AddField(
            model_name="usertrafficlog",
            name="tcp_conn_cnt",
            field=models.IntegerField(default=0, verbose_name="tcp链接数"),
        ),
        migrations.AlterField(
            model_name="usertrafficlog",
            name="proxy_node",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="proxy.proxynode",
                verbose_name="代理节点",
            ),
        ),
        migrations.AlterField(
            model_name="usertrafficlog",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to=settings.AUTH_USER_MODEL,
                verbose_name="用户",
            ),
        ),
        migrations.DeleteModel(
            name="NodeOnlineLog",
        ),
        migrations.DeleteModel(
            name="UserOnLineIpLog",
        ),
    ]