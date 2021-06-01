from flask import *
import json, os, flask_socketio
app = Flask(__name__)
app.config['SECRET_KEY'] = "sdfagsdfg"
socketio = flask_socketio.SocketIO(app)
with open("db/data.json") as fp:
    data = json.load(fp)
with open("db/groups.json") as fp:
    groups = json.load(fp)

# region Add Message To DB

class DB:
    def __init__(self, user, target):
        self.user = user
        self.target = target
    def save_group(self, message):
        group = self.target.lower().replace(" ", "_")
        user = self.user.lower().replace(" ", "_")
        try:
            os.mkdir(f"db/groups/{group}")
        except FileExistsError:
            pass
        try:
            try:
                f = open(f"db/groups/{group}/messages.json")
            except IOError:
                with open(f"db/groups/{group}/messages.json", "w") as f:
                    f.write("{}")
        except FileExistsError:
            pass
        c = json_opener(f"db/groups/{group}/messages.json")
        try:
            c['num'] += 1
        except KeyError:
            c['num'] = 0
        c[str(user) + "-" + str(c['num'])] = str(message)
        with open(f"db/groups/{group}/messages.json", "w+") as fp:
            json.dump(c, fp, indent=True)

        return ""

    def save(self, message):
        user = self.user.lower().replace(" ", "_")
        target = self.target.lower()
        try:
            os.mkdir(f"db/{user}/{target}/")
        except FileExistsError:
            pass
        try:    
            os.mkdir(f"db/{target}/{user}/")
        except FileExistsError:
            pass
        try:
            try:
                f = open(f"db/{user}/{target}/messages.json")
            except IOError:
                with open(f"db/{target}/{user}/messages.json", "w") as f:
                    f.write("{}")
        except FileExistsError:
            pass
        try:
            try:
                f = open(f"db/{target}/{user}/messages.json")
            except IOError:
                with open(f"db/{target}/{user}/messages.json", "w") as f:
                    f.write("{}")
        except FileExistsError:
            pass
        c1 = json_opener(f"db/{user}/{target}/messages.json")
        c2 = json_opener(f"db/{user}/{target}/messages.json")
        try:
            c1['num'] += 1
            c2['num'] += 1
        except KeyError:
            c1['num'] = 0
            c2['num'] = 0
        c1[str(user) + "-" + str(c1['num'])] = str(message)
        c2[str(user) + "-" + str(c2['num'])] = str(message)
        with open(f"db/{target}/{user}/messages.json", "w+") as fp:
            json.dump(c1, fp, indent=True)
        with open(f"db/{user}/{target}/messages.json", "w+") as fp:
            json.dump(c2, fp, indent=True)

        return ""

# endregion

# region index
@app.route('/')
def index():
    global data, groups
    cookie_name = request.cookies.get('name')
    cookie_pw = request.cookies.get('pw')
    if cookie_name != "" and cookie_pw != "" and cookie_name != None and cookie_pw != None:
        try:
            print(cookie_pw)
            if data[cookie_name] == cookie_pw:
                all_users = []
                for j in data.keys():
                    if j.lower() != cookie_name.lower():
                        all_users.append(j)
                all_groups = []
                for i in groups.keys():
                    print(groups)
                    with open(f"db/groups/{i}/participants.json") as fp:
                        c = json.load(fp)
                    if cookie_name in c.keys():
                        all_groups.append(str(i))
                return render_template("home.html", name=cookie_name, pw=cookie_pw, all_users=all_users, all_groups=all_groups)
            else:
                flash("Please Login!", category="error")
                return render_template("auth.html")
        except KeyError:
                flash("Please Login!", category="error")
                return render_template("auth.html")
    else:
        flash("Please Login!", category="error")
        return render_template('auth.html')
# endregion

# region login - Signup
@app.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
    global data, groups
    name = request.form['name'].lower().replace(" ", "_")
    pw = request.form['pw']
    if name != "groups" and name != "data.json" and name != "groups.json" and name != "server":
        with open("db/data.json", "r") as read:
            read = read.read()
            if f'"{name}": ' in read:
                if name in groups.values():
                    flash("Username Taken", category="error")
                    return redirect("/")
            else:
                data[name] = pw
                with open("db/data.json", "w+") as fp:
                    json.dump(data, fp, sort_keys=True, indent=4)
                os.mkdir(f"db/{name}")
                cookie = make_response(redirect("/"))

                cookie.set_cookie('name', name)
                cookie.set_cookie('pw', pw)
                return cookie
    else:
        flash("Username Not Allowed!", category="error")
        return redirect("/")
@app.route('/logout')
def logout():
    cookie = make_response(redirect("/"))
    cookie.set_cookie('name', "")
    cookie.set_cookie('pw', "")
    flash("Logged out!", category="success")
    return cookie

@app.route('/login', methods=['POST', 'GET'])
def login():
    global data, groups
    name = request.form['name'].lower().replace(" ", "_")
    pw = request.form['pw']
    print(pw)
    with open("db/data.json", "r") as read:
        read = read.read()
        if f'"{name}": "{pw}"' in read:
            cookie = make_response(redirect("/"))
            
            cookie.set_cookie('name', name)
            cookie.set_cookie('pw', pw)
            flash("Logged in!", category="success")
            return cookie

        else:
            flash("No Data Stored With This Infos!", category="error")
            return redirect("/")
# endregion

# region search
@app.route('/search$$q=<search>$$me=<me>')
def search(search, me):
    global data, groups
    search = search.lower()
    found = []
    for i in data.keys():
        i = str(i.lower())
        if i.startswith(search) or search.startswith(i) or search in i or i in search or search.endswith(i) or i.endswith(search):
            found.append(i)
        else:
            pass
    for i in groups.keys():
        with open(f"db/groups/{i}/participants.json") as fp:
            c = json.load(fp)
        if me in c.keys():
            if i.startswith(search) or search.startswith(i) or search in i or i in search or search.endswith(i) or i.endswith(search):
                found.append(str(i))
    if found == []:
        return "No Users with this Name"
    founds = {"main":found}
    return jsonify(founds)
# endregion

# region json_opener
def json_opener(path) -> dict:
    with open(path) as fp:
        data = json.load(fp)
        return data
# endregion

# region Go To Chat

@app.route('/chat$$t=<target>$$me=<name>', methods=['POST', 'GET'])
def chat(target, name):
    global groups, data
    print(groups)
    name = name.lower()
    target = target.lower()
    if target in groups.keys():
        group = target.lower().replace(" ", "_")
        user = name.lower().replace(" ", "_")
        try:
            os.mkdir(f"db/groups/{group}")
        except FileExistsError:
            pass
        try:
            try:
                f = open(f"db/groups/{group}/messages.json")
            except IOError:
                with open(f"db/groups/{group}/messages.json", "w") as f:
                    f.write("{}")
        except FileExistsError:
            pass
        with open(f"db/groups/{group}/messages.json") as xl:
            cont = json.load(xl)
        msgs = []
        for i in cont.keys():
            if i != "num":
                n = str(i.split('-')[0])
                if n == user:
                    n = "You"
                msgs.append(n + ": " + cont[i])
        messages = {"main":msgs, "type":"group"}
        return jsonify(messages)


    else:
        try:
            os.mkdir(f"db/{name}/{target}")
        except FileExistsError:
            pass
        try:    
            os.mkdir(f"db/{target}/{name}/")
        except FileExistsError:
            pass
        try:
            try:
                f = open(f"db/{target}/{name}/messages.json")
            except IOError:
                os.system(f"echo  > \"db/{target}/{name}/messages.json\"")
                with open(f"db/{target}/{name}/messages.json", "w") as f:
                    f.write("{}")
        except FileExistsError:
            pass
        try:
            try:
                f = open(f"db/{name}/{target}/messages.json")
            except IOError:
                os.system(f"echo  > \"db/{name}/{target}/messages.json\" ")
                with open(f"db/{name}/{target}/messages.json", "w") as f:
                    f.write("{}")
        except FileExistsError:
            pass
        with open(f"db/{name}/{target}/messages.json") as xl:
            cont = json.load(xl)
        msgs = []
        for i in cont.keys():
            if i != "num":
                n = str(i.split('-')[0])
                if n == name:
                    n = "You"
                msgs.append(n + ": " + cont[i])


        
        messages = {"main":msgs, "type":"dm"}
        return jsonify(messages)

# endregion

# region Send Message
@socketio.on("sent-message")
def send_message(args):
    user = args.split("@$@$")[0].lower().replace(" ", "_")
    msg = args.split("@$@$")[1]
    target = args.split("@$@$")[2].lower().replace(" ", "_")
    if target in groups.keys():
        DB(user, target).save_group(msg)
        socketio.emit(f"{target}-new-message", [target, f"{user}: {msg}"], broadcast=True, include_self=False)
    else:
        DB(user, target).save(msg)
        socketio.emit(f"{target}-new-message", [user, f"{user}: {msg}"], broadcast=True, include_self=False)
# endregion

# region Get Last Message
@app.route('/get-last-msg$$target=<target>$$me=<name>')
def get_last_message(target, name):
    global data, groups
    print(target, name)
    if target not in groups.keys():
        name = name.lower()
        target = target.lower()
        try:
            os.mkdir(f"db/{name}/{target}")
        except FileExistsError:
            pass
        try:    
            os.mkdir(f"db/{target}/{name}/")
        except FileExistsError:
            pass
        try:
            try:
                f = open(f"db/{target}/{name}/messages.json")
            except IOError:
                os.system(f"echo  > \"db/{target}/{name}/messages.json\"")
                with open(f"db/{target}/{name}/messages.json", "w") as f:
                    f.write("{}")
        except FileExistsError:
            pass
        try:
            try:
                f = open(f"db/{name}/{target}/messages.json")
            except IOError:
                os.system(f"echo  > \"db/{name}/{target}/messages.json\" ")
                with open(f"db/{name}/{target}/messages.json", "w") as f:
                    f.write("{}")
        except FileExistsError:
            pass
        with open(f"db/{name}/{target}/messages.json") as xl:
            cont = json.load(xl)
        var = list(cont)[-1]
        d = {'main':cont[str(var)]}
        print(d)
        return jsonify(d)
    else:
        name = name.lower()
        target = target.lower()
        try:
            try:
                f = open(f"db/groups/{target}/messages.json")
            except IOError:
                os.system(f"echo  > \"db/groups/{target}/messages.json\"")
                with open(f"db/groups/{target}/messages.json", "w") as f:
                    f.write("{}")
        except FileExistsError:
            pass
        try:
            try:
                f = open(f"db/groups/{target}/participants.json")
            except IOError:
                os.system(f"echo  > \"db/groups/{target}/participants.json\"")
                with open(f"db/groups/{target}/participants.json", "w") as f:
                    f.write("{}")
        except FileExistsError:
            pass
        with open(f"db/groups/{target}/messages.json") as xl:
            cont = json.load(xl)
        var = list(cont)[-1]
        d = {'main':cont[str(var)]}
        print(d)
        return jsonify(d)
        # return jsonify({"main":""})

# endregion

# region Typing
@socketio.on("typing")
def typing(args):
    target = args.split("@$@$")[0]
    name = args.split("@$@$")[1]
    socketio.emit(f"{target}-typing", name, broadcast=True, include_self=False)
@socketio.on("stop-typing")
def stop_typing(args):
    target = args.split("@$@$")[0]
    name = args.split("@$@$")[1]
    socketio.emit(f"{target}-stop-typing", name, broadcast=True, include_self=False)
# endregion

# region Groups
@app.route('/create-group', methods=['GET', 'POST'])
def create_group():
    global data, groups
    if request.method == "POST":
        owner:str = request.form['owner']
        name:str = request.form['name']
        pw:str = request.form['pw']
        if name not in groups.values() and name != "no_need" and name not in data.values():
            groups[name] = [owner, pw]
            with open("db/groups.json", "w+") as fp:
                json.dump(groups, fp, sort_keys=True, indent=4)
            os.mkdir(f"db/groups/{name}")
            try:
                try:
                    f = open(f"db/groups/{name}/messages.json")
                except IOError:
                    os.system(f"echo  > \"db/groups/{name}/messages.json\"")
                    with open(f"db/groups/{name}/messages.json", "w") as f:
                        f.write("{}")
            except FileExistsError:
                pass
            try:
                try:
                    f = open(f"db/groups/{name}/participants.json")
                except IOError:
                    os.system(f"echo  > \"db/groups/{name}/participants.json\"")
                    with open(f"db/groups/{name}/participants.json", "w") as f:
                        f.write("{}")
            except FileExistsError:
                pass

            parts = json_opener(f"db/groups/{name}/participants.json")
            parts[owner] = "owner"
            with open(f"db/groups/{name}/participants.json", "w+") as fp:
                json.dump(parts, fp, sort_keys=True, indent=4)
            flash("Group Created!", category="success")
            return redirect("/")
        else:
            flash("Name Already Taken!", category="error")
            return redirect("/")
    else:
        cookie_name = request.cookies.get('name')
        cookie_pw = request.cookies.get('pw')
        if cookie_name != "" and cookie_pw != "" and cookie_name != None and cookie_pw != None:
            try:
                if data[cookie_name] == cookie_pw:
                    return render_template("new-group.html", name=cookie_name, pw=cookie_pw)
                else:
                    return render_template("auth.html")
            except KeyError:
                    return render_template("auth.html")
        else:
            return render_template('auth.html')

@app.route('/invite$$group=<group>')
def group_invite(group):
    global data, groups
    me = request.cookies.get('name').lower().replace(" ", "_")
    if me == "" or me == None:
        return redirect("/")
    group = group.lower().replace(" ", "_")
    try:
        p = json_opener(f"db/groups/{group}/participants.json")
        if str(me.replace(" ", "_").lower()) in data.keys():
            if me not in p.keys():
                p[me] = "participant"
                with open(f"db/groups/{group}/participants.json", "w+") as fp:
                    json.dump(p, fp, indent=True)
                DB("Server", group).save_group(f"{me} Joined!")
                flash(f"Joined {group}", category="success")
                return redirect("/")
            else:
                flash(f"You are already in {group}", category="error")
                return redirect("/")
        else:
            flash("Invalid invite link!", category="error")
            return redirect("/")
    except KeyError:
        flash("Invalid invite link!", category="error")
        return redirect("/")

@app.route('/get-parts$$group=<group>')
def get_parts(group):
    p = json_opener(f"db/groups/{group}/participants.json")
    f = []
    for i in p.keys():
        f.append(i)
    res = {"main":f}
    print("------------------")
    print(res)
    return jsonify(res)

@app.route('/leave$$g=<group>$$me=<name>$jinjadfdjnsadfkj$$pw=<pw>', methods=['GET', 'POST'])
def leave_group(group, name, pw):
    global data, groups
    if group in groups.keys():
        try:
            if data[name] == pw:
                try:
                    try:
                        f = open(f"db/groups/{group}/messages.json")
                    except IOError:
                        os.system(f"echo  > \"db/groups/{group}/messages.json\"")
                        with open(f"db/groups/{group}/messages.json", "w") as f:
                            f.write("{}")
                except FileExistsError:
                    pass
                try:
                    try:
                        f = open(f"db/groups/{group}/participants.json")
                    except IOError:
                        os.system(f"echo  > \"db/groups/{group}/participants.json\"")
                        with open(f"db/groups/{group}/participants.json", "w") as f:
                            f.write("{}")
                except FileExistsError:
                    pass
                p = json_opener(f"db/groups/{group}/participants.json")
                if name in p.keys():
                    del p[name]
                    with open(f"db/groups/{group}/participants.json", "w+") as fp:
                        json.dump(p, fp, indent=True)
                    flash(f"Left {group}!")
                    return redirect('/')
                else:
                    flash("You are not in " + group + "!")
                    return redirect("/")
            else:
                flash("Please Login!", category="error")
                return redirect("/") 
        except KeyError:
            flash("Please Login!", category="error")
            return redirect("/") 
    else:
        flash("Group Does not exist!", category="error")
        return redirect("/")

# endregion

if __name__ == '__main__':
    print(" * http://localhost:5000")
    socketio.run(app, host='localhost', debug=True)
# if __name__ == '__main__':
    # import subprocess
    # subprocess.Popen(["python", "flasktest.py"])
    # subprocess.Popen(['npm', 'install', '-g', 'localtunnel'])
    # subprocess.Popen(
    #     ['npx', 'localtunnel', '--subdomain', 'whatsapp-clone', '--port', '80'])
    # socketio.run(app, host="localhost", port=80, debug=True)