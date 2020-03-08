from . import api
from app import app, db
import os
from flask import Flask, render_template, request, url_for, jsonify
from flask_restful import Api, Resource
from app.models import log
import json
import datetime

api = Api(app)

'''
    通过url接受参数
'''


class Logs(Resource):
    # 增添备忘录，获取前端发送的参数
    # info:文本内容
    # deadtime:截至时间
    def post(self):
        if "info" not in request.args or "deadtime" not in request.args:
            return jsonify({"status": 4001})
        data = {
            "info": request.args["info"],
            "deadtime": request.args["deadtime"]
        }
        try:
            tm = datetime.datetime.strptime(data["deadtime"], "%Y-%m-%d %H:%M:%S")
        except:
            return jsonify({"status": 4002})
        lg = log(
            info=data['info'],
            ok=0,
            deadtime=tm
        )
        db.session.add(lg)
        db.session.commit()
        return jsonify({"status": 200})

    def put(self):
        if "class" not in request.args or "op" not in request.args:
            return jsonify({"status": 4001})
        try:
            data = {
                "class": eval(request.args["class"]),
                "op": eval(request.args["op"]),
                "id": 0
            }
        except:
            return jsonify({"status": 4002})
        if data["class"] != 1 and data["class"] != 2:
            return jsonify({"status": 4002})
        if data["op"] != 1 and data["op"] != 0:
            return jsonify({"status": 4002})

        # 一条
        if data["class"] == 1:
            if "id" not in request.args:
                return jsonify({"status": 4001})
            try:
                id = eval(request.args["id"])
            except:
                return jsonify({"status": 4002})
            print(id)
            lg = log.query.filter_by(id=id).first()
            if lg == None:
                return jsonify({"status": 4003})
            # 一条-->已完成
            if data["op"] == 1:
                lg.ok = 1
            # 一条-->未完成
            if data["op"] == 0:
                lg.ok = 0
            db.session.add(lg)
            db.session.commit()
            return jsonify({"status": "200"})
        # 全部
        if data["class"] == 2:
            logs = log.query.order_by(
                log.addtime.desc()
            )
            # 全部-->已完成
            ope = 1
            # 全部-->未完成
            if data["op"] == 0:
                ope = 0
            for it in logs:
                it.ok = ope
                db.session.add(it)
                db.session.commit()

    def get(self):
        if "op" not in request.args or "class" not in request.args:
            return jsonify({"status": 4001})
        # 查询操作
        try:
            data = {
                "op": eval(request.args["op"]),
                "class": eval(request.args["class"])
            }
        except:
            return jsonify({"status": 4002})
        if data["class"] != 1 and data["class"] != 2 and data["class"] != 0:
            return jsonify({"status": 4002})
        if data["op"] != 1 and data["op"] != 0:
            return jsonify({"status": 4002})
        # 查询数目
        if data["op"] == 0:
            num = 0
            if data["class"] == 1:
                num = log.query.filter_by(ok=1).count()
            if data["class"] == 0:
                num = log.query.filter_by(ok=0).count()
            if data["class"] == 2:
                num = log.query.filter_by(ok=0).count() + log.query.filter_by(ok=1).count()
            return jsonify({"status": 200, "num": num})
        if data["op"] == 1:
            lit = []
            if data["class"] == 1:
                logs = log.query.filter_by(ok=1)
            if data["class"] == 0:
                logs = log.query.filter_by(ok=0)
            if data["class"] == 2:
                logs = log.query.order_by(
                    log.addtime.desc()
                )
            for lg in logs:
                jsn = {"id": lg.id,
                       "info": lg.info,
                       "ok": lg.ok,
                       "addtime": str(lg.addtime),
                       "deadtime": str(lg.deadtime)
                       }
                lit.append(jsn)
            return jsonify({"status": 200, "data": lit})

    def delete(self):
        if "class" not in request.args:
            return jsonify({"status":4001})
        data = {
            "class": eval(request.args["class"]),
        }
        if data["class"] <0 or data["class"]>3:
            return jsonify({"status":4002})
        # 全删
        if data["class"] == 0:
            logs = log.query.order_by(
                log.addtime.desc()
            )
            for it in logs:
                db.session.delete(it)
                db.session.commit()
            return jsonify({"status": 200})
        # 删已完成
        if data["class"] == 1:
            logs = log.query.order_by(
                log.addtime.desc()
            )
            for it in logs:
                if it.ok == 0:
                    continue
                db.session.delete(it)
                db.session.commit()
            return jsonify({"status": 200})
        # 删未完成
        if data["class"] == 2:
            logs = log.query.order_by(
                log.addtime.desc()
            )
            for it in logs:
                if it.ok == 1:
                    continue
                db.session.delete(it)
                db.session.commit()
            return jsonify({"status": 200})
        # 删一条
        if data["class"] == 3:
            id = eval(request.args["id"])
            print(id)
            lg = log.query.filter_by(id=id).first()
            if lg == None:
                return jsonify({"status": 4003})
            db.session.delete(lg)
            db.session()
            return jsonify({"status": 200})
        return jsonify({"status": 4002})


'''
    通过接受前端传来的json获取参数
'''


class Log(Resource):
    # 增添备忘录，获取前端发送的json
    # info:文本内容
    # deadtime:截至时间
    def post(self):
        data=json.loads(request.get_data(as_text=True))
        if "info" not in data or "deadtime" not in data:
            return jsonify({"status": 4001})
        try:
            tm = datetime.datetime.strptime(data["deadtime"], "%Y-%m-%d %H:%M:%S")
        except:
            return jsonify({"status": 4002})
        lg = log(
            info=data['info'],
            ok=0,
            deadtime=tm
        )
        db.session.add(lg)
        db.session.commit()
        return jsonify({"status": 200})

    def put(self):
        data = json.loads(request.get_data(as_text=True))
        if "class" not in data or "op" not in data:
            return jsonify({"status": 4001})
        try:
            data = {
                "class": eval(data["class"]),
                "op": eval(data["op"]),
                "id": 0
            }
        except:
            return jsonify({"status": 4002})
        if data["class"] != 1 and data["class"] != 2:
            return jsonify({"status": 4002})
        if data["op"] != 1 and data["op"] != 0:
            return jsonify({"status": 4002})

        # 一条
        if data["class"] == 1:
            if "id" not in data:
                return jsonify({"status": 4001})
            try:
                id = eval(data["id"])
            except:
                return jsonify({"status": 4002})
            print(id)
            lg = log.query.filter_by(id=id).first()
            if lg == None:
                return jsonify({"status": 4003})
            # 一条-->已完成
            if data["op"] == 1:
                lg.ok = 1
            # 一条-->未完成
            if data["op"] == 0:
                lg.ok = 0
            db.session.add(lg)
            db.session.commit()
            return jsonify({"status": "200"})
        # 全部
        if data["class"] == 2:
            logs = log.query.order_by(
                log.addtime.desc()
            )
            # 全部-->已完成
            ope = 1
            # 全部-->未完成
            if data["op"] == 0:
                ope = 0
            for it in logs:
                it.ok = ope
                db.session.add(it)
                db.session.commit()

    def get(self):
        data = json.loads(request.get_data(as_text=True))
        if "op" not in data or "class" not in data:
            return jsonify({"status": 4001})
        # 查询操作
        try:
            data = {
                "op":data["op"],
                "class": data["class"]
            }
        except:
            return jsonify({"status": 4002})
        if data["class"] != 1 and data["class"] != 2 and data["class"] != 0:
            return jsonify({"status": 4002})
        if data["op"] != 1 and data["op"] != 0:
            return jsonify({"status": 4002})
        # 查询数目
        if data["op"] == 0:
            num = 0
            if data["class"] == 1:
                num = log.query.filter_by(ok=1).count()
            if data["class"] == 0:
                num = log.query.filter_by(ok=0).count()
            if data["class"] == 2:
                num = log.query.filter_by(ok=0).count() + log.query.filter_by(ok=1).count()
            return jsonify({"status": 200, "num": num})
        if data["op"] == 1:
            lit = []
            if data["class"] == 1:
                logs = log.query.filter_by(ok=1)
            if data["class"] == 0:
                logs = log.query.filter_by(ok=0)
            if data["class"] == 2:
                logs = log.query.order_by(
                    log.addtime.desc()
                )
            for lg in logs:
                jsn = {"id": lg.id,
                       "info": lg.info,
                       "ok": lg.ok,
                       "addtime": str(lg.addtime),
                       "deadtime": str(lg.deadtime)
                       }
                lit.append(jsn)
            return jsonify({"status": 200, "data": lit})

    def delete(self):
        data = json.loads(request.get_data(as_text=True))
        if "class" not in data:
            return jsonify({"status": 4001})
        data = {
            "class": eval(data["class"]),
        }
        if data["class"] < 0 or data["class"] > 3:
            return jsonify({"status": 4002})
        # 全删
        if data["class"] == 0:
            logs = log.query.order_by(
                log.addtime.desc()
            )
            for it in logs:
                db.session.delete(it)
                db.session.commit()
            return jsonify({"status": 200})
        # 删已完成
        if data["class"] == 1:
            logs = log.query.order_by(
                log.addtime.desc()
            )
            for it in logs:
                if it.ok == 0:
                    continue
                db.session.delete(it)
                db.session.commit()
            return jsonify({"status": 200})
        # 删未完成
        if data["class"] == 2:
            logs = log.query.order_by(
                log.addtime.desc()
            )
            for it in logs:
                if it.ok == 1:
                    continue
                db.session.delete(it)
                db.session.commit()
            return jsonify({"status": 200})
        # 删一条
        if data["class"] == 3:
            id = eval(data["id"])
            print(id)
            lg = log.query.filter_by(id=id).first()
            if lg == None:
                return jsonify({"status": 4003})
            db.session.delete(lg)
            db.session()
            return jsonify({"status": 200})
        return jsonify({"status": 4002})


api.add_resource(Log, "/log", endpoint='log')
api.add_resource(Logs, "/logs", endpoint='logs')


@app.route("/")
def index():
    return render_template("test.html")
