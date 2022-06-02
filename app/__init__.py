#coding:utf-8
from flask import Flask, redirect, url_for, request
from datetime import datetime
from flask_bootstrap import Bootstrap
from app.config_default import Config as DefaultConfig


bootstrap = Bootstrap()

def check_start(app, db):
    from app.includes.start import _exist_config, exist_table, create_path, set_site
    create_path(app)
    #表示是否可以开始使用
    app.start = False
    #是否配置了数据库
    if _exist_config(app):
        from app.config import Config
        #配置数据库
        app.config.from_object(Config)
        #是否存在要连接的数据表
        if exist_table(app):
            app.start = True
            return
    @app.before_request
    def request_check_start():
        #创建站点名字和值
        if app.start:
            return set_site(app)
        ends = frozenset(["admin.setup", "admin.install", "static"])
        if request.endpoint in ends:
            return
        if not _exist_config(app):
            return redirect(url_for("admin.setup"))
        return redirect(url_for("admin.install"))

#首页书籍列表xx时间前更新
def template_filters(app):
    @app.template_filter("friendly_time")
    def friendly_time(date):
        now = datetime.now()
        delta = now - date
        if delta.days >= 365:
            return u'%d年前' % (delta.days / 365)
        elif delta.days >= 30:
            return u'%d个月前' % (delta.days / 30)
        elif delta.days > 0:
            return u'%d天前' % delta.days
        elif delta.days < 0:
            return u"0秒前"
        elif delta.seconds < 60:
            return u"%d秒前" % delta.seconds
        elif delta.seconds < 60 * 60:
            return u"%d分钟前" % (delta.seconds / 60)
        else:
            return u"%d小时前" % (delta.seconds / 60 / 60)

#创建一个应用
def create_app():
    app = Flask(__name__)
    app.config.from_object(DefaultConfig)

    from app.models.model import db, login_manager

    #网页前端框架
    bootstrap.init_app(app)
    db.init_app(app)
    db.PREFIX = app.config["DB_PREFIX"]

    app.site = {}
    def site_context_processor():
        return dict(site=app.site)
    app.context_processor(site_context_processor)
    check_start(app, db)

    login_manager.init_app(app)

    #蓝图——web,admin,api
    from app.web import web
    app.register_blueprint(web)

    # url_prefix会添加到所有与该蓝图关联的URL前面。
    from app.admin import admin
    app.register_blueprint(admin, url_prefix="/admin")

    from app.api import api
    app.register_blueprint(api, url_prefix="/api")

    template_filters(app)

    login_manager.login_view = "admin.login"
    login_manager.login_message = "请先登录!!!"

    #日志
    from app.log  import init_logging
    init_logging(app)

    return app


