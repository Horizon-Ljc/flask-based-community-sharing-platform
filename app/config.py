#coding: utf-8
from app.config_default import Config as DefaultConfig

class Config(DefaultConfig):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:abc123@47.98.171.135/beibq?charset=utf8'

