from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django_telegram_login.authentication import verify_telegram_authentication
from django_telegram_login.errors import (
    NotTelegramDataError,
    TelegramDataIsOutdatedError,
)

from apps.constants import THEME_CHOICES
from apps.proxy.models import ProxyNode
from apps.sspanel.forms import LoginForm, RegisterForm, TGLoginForm
from apps.sspanel.models import (
    Announcement,
    Donate,
    Goods,
    InviteCode,
    MoneyCode,
    PurchaseHistory,
    RebateRecord,
    Ticket,
    User,
    UserSocialProfile,
)
from apps.utils import traffic_format


class IndexView(View):
    def get(self, request):
        """跳转到首页"""
        context = {"simple_extra_static": True}
        return render(request, "web/index.html", context=context)


class HelpView(View):
    def get(self, request):
        """跳转到帮助界面"""
        context = {"simple_extra_static": True}
        return render(request, "web/help.html", context=context)


class RegisterView(View):
    def get(self, request):
        context = {"simple_extra_static": True}
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("sspanel:userinfo"))
        if request.GET.get("ref"):
            form = RegisterForm(initial={"ref": request.GET.get("ref")})
        else:
            form = RegisterForm(initial={"invitecode": request.GET.get("invitecode")})
        context["form"] = form
        return render(request, "web/register.html", context=context)

    def post(self, request):
        context = {"simple_extra_static": True}
        if not settings.ALLOW_REGISTER:
            return HttpResponse("已经关闭注册了")

        form = RegisterForm(data=request.POST)
        if form.is_valid():
            user = User.add_new_user(form.cleaned_data)
            if not user:
                messages.error(request, "服务出现了点小问题", extra_tags="请尝试或者联系站长~")
                return render(request, "web/register.html", {"form": form})
            else:
                messages.success(request, "自动跳转到用户中心", extra_tags="注册成功！")
                user = authenticate(
                    username=form.cleaned_data["username"],
                    password=form.cleaned_data["password1"],
                )
                login(request, user)
                return HttpResponseRedirect(reverse("sspanel:userinfo"))
        context["form"] = form
        return render(request, "web/register.html", context=context)


class UserLogInView(View):
    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user and user.is_active:
                login(request, user)
                messages.success(request, "自动跳转到用户中心", extra_tags="登录成功！")
                return HttpResponseRedirect(reverse("sspanel:userinfo"))
            else:
                messages.error(request, "请重新填写信息！", extra_tags="登录失败！")

        context = {"form": LoginForm(), "simple_extra_static": True}
        return render(request, "web/login.html", context=context)

    def get(self, request):
        context = {"form": LoginForm(), "simple_extra_static": True}
        return render(request, "web/login.html", context=context)


class TelegramLoginView(View):
    def get(self, request):
        try:
            result = verify_telegram_authentication(
                bot_token=settings.TELEGRAM_BOT_TOKEN, request_data=request.GET
            )
        except TelegramDataIsOutdatedError:
            return HttpResponseBadRequest(
                "Authentication was received more than a day ago."
            )
        except NotTelegramDataError:
            return HttpResponseBadRequest("The data is not related to Telegram!")

        if "username" in result:
            tg_username = result["username"]
        else:
            tg_username = (
                result.get("first_name", "") + " " + result.get("last_name", "")
            )

        # 已经绑定过了
        usp = UserSocialProfile.get_or_create_and_update_info(
            UserSocialProfile.TYPE_TG, tg_username, result
        )
        if usp.user_id:
            login(
                request,
                usp.user,
                backend="django.contrib.auth.backends.ModelBackend",
            )
            messages.success(request, "自动跳转到用户中心", extra_tags="登录成功！")
            return HttpResponseRedirect(reverse("sspanel:userinfo"))
        # 需要渲染绑定页面
        context = {
            "form": TGLoginForm(initial={"tg_username": tg_username}),
        }
        return render(request, "web/telegram_login.html", context)

    def post(self, request):
        form = TGLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            usp = UserSocialProfile.get_by_platform(
                UserSocialProfile.TYPE_TG, form.cleaned_data["tg_username"]
            )
            if user and user.is_active and usp:
                with transaction.atomic():
                    login(request, user)
                    usp.bind(user)
                messages.success(request, "自动跳转到用户中心", extra_tags="绑定成功！")
                return HttpResponseRedirect(reverse("sspanel:userinfo"))
            else:
                messages.error(request, "账户不存在(请先注册)/密码不正确！", extra_tags="绑定失败！")

        return HttpResponseRedirect(reverse("sspanel:login"))


class UserLogOutView(View):
    def get(self, request):
        logout(request)
        messages.warning(request, "欢迎下次再来", extra_tags="注销成功")
        return HttpResponseRedirect(reverse("sspanel:index"))


class InviteCodeView(View):
    def get(self, request):
        code_list = InviteCode.list_by_code_type(InviteCode.TYPE_PUBLIC)
        return render(request, "web/invite.html", context={"code_list": code_list})


class AffInviteView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        rebate_logs = RebateRecord.list_by_user_id_with_consumer_username(user.pk)
        bar_config = {
            "labels": ["z", "v", "x", "x", "z", "v", "x", "x", "z", "v"],
            "data": [1, 2, 3, 4, 1, 1, 1, 1, 1, 2],
            "data_title": "每日邀请注册人数",
        }
        context = {
            "invite_percent": settings.INVITE_PERCENT * 100,
            "ref_link": user.ref_link,
            "bar_config": bar_config,
            "rebate_logs": rebate_logs,
        }
        return render(request, "web/aff_invite.html", context=context)


class UserInfoView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        anno = Announcement.objects.first()
        min_traffic = traffic_format(settings.MIN_CHECKIN_TRAFFIC)
        max_traffic = traffic_format(settings.MAX_CHECKIN_TRAFFIC)
        user_active_nodes = ProxyNode.get_active_nodes(user.level)
        user_active_nodes_types = {node.node_type for node in user_active_nodes}
        if len(user_active_nodes_types) > 1:
            user_active_nodes_types.add("all")
        context = {
            "user": user,
            "anno": anno,
            "min_traffic": min_traffic,
            "max_traffic": max_traffic,
            "themes": THEME_CHOICES,
            "sub_link": user.sub_link,
            "active_node_count": user_active_nodes.count(),
            "active_node_types": user_active_nodes_types,
            "usp_list": UserSocialProfile.list_by_user_id(user.id),
        }
        Announcement.send_first_visit_msg(request)
        return render(request, "web/user_info.html", context=context)


class UserSubCenterView(LoginRequiredMixin, View):
    def get(self, request):
        context = {
            "user": request.user,
            "sub_link": request.user.sub_link,
        }
        return render(request, "web/user_sub_center.html", context=context)


class UserTrafficLogView(LoginRequiredMixin, View):
    def get(self, request):
        node_list = ProxyNode.get_active_nodes()
        context = {"user": request.user, "node_list": node_list}
        return render(request, "web/user_traffic_log.html", context=context)


class ShopView(LoginRequiredMixin, View):
    def get(self, request):
        context = {
            "user": request.user,
            "goods": Goods.get_user_can_buy_goods(request.user),
            "records": PurchaseHistory.objects.filter(user=request.user)[:10],
        }
        return render(request, "web/shop.html", context=context)


class ClientView(LoginRequiredMixin, View):
    def get(self, request):
        """跳转到客户端界面"""
        return render(request, "web/client.html")


class PurchaseLogView(LoginRequiredMixin, View):
    def get(self, request):
        """用户购买记录页面"""

        records = PurchaseHistory.objects.filter(user=request.user)[:10]
        context = {"records": records}
        return render(request, "web/purchaselog.html", context=context)


class ChargeView(LoginRequiredMixin, View):
    def get(self, request):
        """充值界面的跳转"""
        user = request.user
        codelist = MoneyCode.objects.filter(user=user)
        donatelist = Donate.objects.all()[:8]
        context = {"user": user, "codelist": codelist, "donatelist": donatelist}
        return render(request, "web/charge_center.html", context=context)

    @transaction.atomic
    def post(self, request):
        user = request.user
        input_code = request.POST.get("chargecode")
        # 在数据库里检索充值
        code = MoneyCode.objects.filter(code=input_code).first()
        # 判断充值码是否存在
        if not code:
            messages.error(request, "请重新获取充值码", extra_tags="充值码失效")
            return HttpResponseRedirect(reverse("sspanel:chargecenter"))
        else:
            # 判断充值码是否被使用
            if code.isused is True:
                # 当被使用的是时候
                messages.error(request, "请重新获取充值码", extra_tags="充值码失效")
                return HttpResponseRedirect(reverse("sspanel:chargecenter"))
            else:
                # 充值操作
                user.balance += code.number
                code.user = user.username
                code.isused = True
                user.save()
                code.save()
                messages.success(request, "请去商店购买商品！", extra_tags="充值成功！")
                return HttpResponseRedirect(reverse("sspanel:chargecenter"))


class AnnouncementView(LoginRequiredMixin, View):
    def get(self, request):
        """网站公告列表"""
        anno = Announcement.objects.all()
        return render(request, "web/announcement.html", {"anno": anno})


class TicketsView(LoginRequiredMixin, View):
    def get(self, request):
        """工单系统"""
        ticket = Ticket.objects.filter(user=request.user)
        context = {"ticket": ticket}
        return render(request, "web/ticket.html", context=context)


class TicketCreateView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "web/ticket_create.html")

    def post(self, request):
        """工单提交"""
        title = request.POST.get("title", "")
        body = request.POST.get("body", "")
        Ticket.objects.create(user=request.user, title=title, body=body)
        messages.success(request, "数据更新成功！", extra_tags="添加成功")
        return HttpResponseRedirect(reverse("sspanel:tickets"))


class TicketDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        """工单编辑"""
        ticket = Ticket.objects.get(pk=pk)
        context = {"ticket": ticket}
        return render(request, "web/ticket_edit.html", context=context)

    def post(self, request, pk):
        ticket = Ticket.objects.get(pk=pk)
        ticket.title = request.POST.get("title", "")
        ticket.body = request.POST.get("body", "")
        ticket.save()
        messages.success(request, "数据更新成功", extra_tags="修改成功")
        return HttpResponseRedirect(reverse("sspanel:tickets"))


class TicketDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        """删除指定"""
        ticket = Ticket.objects.filter(pk=pk, user=request.user).first()
        if ticket:
            ticket.delete()
            messages.success(request, "该工单已经删除", extra_tags="删除成功")
        else:
            messages.error(request, "该工单不存在", extra_tags="删除失败")
        return HttpResponseRedirect(reverse("sspanel:tickets"))
