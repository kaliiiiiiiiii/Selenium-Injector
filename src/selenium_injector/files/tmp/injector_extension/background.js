// Forcing service worker to stay alive by sending a "ping" to a port where noone is listening
// Essentially it prevents SW to fall asleep after the first 30 secs of work.

    const INTERNAL_STAYALIVE_PORT = "Whatever_Port_Name_You_Want"
    var alivePort = null;
    StayAlive();

    async function StayAlive() {
    var lastCall = Date.now();
    var wakeup = setInterval( () => {

        const now = Date.now();
        const age = now - lastCall;

        if (alivePort == null) {
            alivePort = chrome.runtime.connect({name:INTERNAL_STAYALIVE_PORT})

            alivePort.onDisconnect.addListener( (p) => {
                alivePort = null;
            });
        }

        if (alivePort) {
            alivePort.postMessage({content: "ping"});
        }
    }, 25000);
}

// chrome extension libs

globalThis.proxy = {}

proxy.set = function(scheme,host,port, patch_webrtc = true, patch_location=true, bypass_list=["localhost"]){
    proxy.config = {
        mode: "fixed_servers",
        rules: {
           singleProxy: {
             scheme: scheme,
             host: host,
             port: port
           },
          bypassList: bypass_list
        }
    };
    chrome.proxy.settings.set({value: proxy.config, scope: "regular"}, function() {});
    if (patch_webrtc){webrtc_leak.disable();};
    if(patch_location){contentsettings.set_location("block")}
}

proxy.get = function(){
    connection.not_return = true;
    chrome.proxy.settings.get({'incognito': false}, connection.send_back.bind(connection));
}

proxy.clear = function(clear_webrtc=true, clear_location=true){
    chrome.proxy.settings.clear({});
    if(clear_webrtc){webrtc_leak.clear();}
    if (clear_location){contentsettings.set_location("allow")}
    delete(proxy.config)
}


proxy.set_auth = function(username, password, urls=["<all_urls>"]){
    proxy.auth_call = function (details) {
        return {
            authCredentials: {
                username: username,
                password: password
            }
        };
    }
    chrome.webRequest.onAuthRequired.addListener(
            proxy.auth_call,
            {urls: urls},
            ['blocking']
    );
}

proxy.clear_auth = function(urls=["<all_urls>"]){
   chrome.webRequest.onAuthRequired.removeListener(
            proxy.auth_call,
            {urls: urls},
            ['blocking']);
   delete(proxy.auth_call)
}

globalThis.webrtc_leak = {}

webrtc_leak.disable = function(value="disable_non_proxied_udp"){
      // https://github.com/aghorler/WebRTC-Leak-Prevent
      chrome.privacy.network.webRTCIPHandlingPolicy.set({
            "value": value
          });
}

webrtc_leak.clear = function(){
      webrtc_leak.disable("default")
}

globalThis.contentsettings = {}

contentsettings.set = function(setting,value, urls="<all_urls>"){
    chrome.contentSettings[setting].set({"primaryPattern":urls,"setting":value}, console.log)
}

contentsettings.set_location = function(setting = "ask",urls="<all_urls>"){
    contentsettings.set("location", setting, urls)
}


class DefaultDict {
  constructor(defaultVal) {
    return new Proxy({}, {
      get: (target, name) => name in target ? target[name] : defaultVal
    })
  }
}

class connector {
  constructor(host, port, username) {
    this.connection = {}
    this.connection.host = host;
    this.connection.port = port;
    this.connection.username = username;
  }

// structs

isFunction(functionToCheck) {
 return functionToCheck && {}.toString.call(functionToCheck) === '[object Function]';
}

// connection to python

connect(){
    this.connection.socket = new WebSocket("ws://"+this.connection.host+":"+parseInt(this.connection.port));
      this.connection.socket.addEventListener("open", (event) => {
        this.connection.socket.send(this.connection.username);
        this.connection.socket.addEventListener("message", (event) => {
            this.handler(event.data)
            });
        });
      this.connection.socket.addEventListener("error", (event) => {this.connect()});
      this.connection.socket.addEventListener("close", (event) => {this.connect()});
}

send_back(...results) {
    var response = '{"result":'+this.stringify(results)+', "status":'+JSON.stringify(this.status)+'}';
    console.log({"response":JSON.parse(response)});
    this.connection.socket.send(response)
}

handler(request){
        var request = JSON.parse(request);
        console.log({"request":request})
        this.not_return = request["not_return"]
        this.status = 200
        try{var result = this.eval(request)}catch(e){
            var result={"message":e.message,"stack":e.stack};
            this.status="error"};
        if(this.not_return){if(e){throw e}}
        else{this.send_back(result)}
}

eval(type_json){
    var defaultdict = new DefaultDict(undefined)
    var type_json = Object.assign({}, defaultdict, type_json)
    var type = type_json["type"];
    switch (type) {
        case "type":
            var result = this.eval(type_json["type_json"]);
            break;
        case "path":
            var result = this.path(type_json["path"], type_json["obj"]);
            break;
        case "exec":
            var result = this.exec(type_json["func"], type_json["args"]);
            break;
        case "val":
            var result = type_json["val"];
            break;
        case "if":
            var result = this.if_else(type_json["if"],type_json["do"],type_json["else"]);
            break;
        case "list":
            var result = this.list(type_json["list"]);
            break;
        case "dict":
            var result = this.dict(type_json["dict_list"]);
            break;
        case "op":
            var result = this.op(type_json["op"], this.eval(type_json["a"]), this.eval(type_json["b"]));
            break;
        case "this":
            var result = this
            break;
        default:
            throw new TypeError("Expected type_json, but got "+this.stringify(type_json));
    }
    return result;
}

path(path, obj = undefined){
    if (obj == undefined){obj = globalThis} else{obj = this.eval(obj)}
    for (var i=0, path=path.split('.'), len=path.length; i<len; i++){
        if(this.isFunction(obj[path[i]])){obj = obj[path[i]].bind(obj)}
        else{obj = obj[path[i]]};
    };
    return obj;
}

exec(func, args=[]){
    var res_args = [];
    var do_eval = this.eval.bind(this)
    args.forEach(function (item, index) {
        res_args.push(do_eval(item))
    });
    var res_func = this.eval(func)
    if (this.isFunction(res_func)){
        return res_func(...res_args)
    }
    else{
        throw new TypeError("Expected a function, got "+this.stringify(res_func))
    };
}

list(list){
    var results = [];
    list.forEach(function(item, index){
        results.push(this.eval(item))
    });
    return results
}

dict(dict_list){
    var res_dict = {};
    dict_list.forEach(function(item) {
        res_dict[this.eval(item["key"])] = this.eval(item["val"])
    });
    return res_dict
}

if_else(condition, statement, else_statement=undefined){
    if (this.eval(condition)){
        var result = this.eval(statement)
    }
    else {
        if (else_statement == undefined){
            var result = undefined
        }
        else {
            var result = this.eval(else_statement)
        }
    };
    return result
}

stringify(obj){
    var result = JSON.stringify(obj, this.replacer.bind(this))
    return result
}

replacer(key, value) {
  // Filtering out properties
  if (this.isFunction(value)) {
    this.status = "func_to_str"
    return value.toLocaleString();
  }
  else if (value == undefined){
    return null
  }
  else {
    return value
  }
}

op(op, a, b) {
      function num(x) {
        if (typeof x != "number")
          throw new Error("Expected number but got " + x);
        return x;
      }
      function div(x) {
        if (num(x) == 0)
          throw new Error("Divide by zero");
        return x;
      }
      var a = this.eval(a)
      var b = this.eval(b)
      switch (op) {
        case "+":
          return a + b;
        case "-":
          return num(a) - num(b);
        case "*":
          return num(a) * num(b);
        case "/":
          return num(a) / div(b);
        case "%":
          return num(a) % div(b);
        case "&&":
          return a && b;
        case "||":
          return a || b;
        case "|":
          return a | b;
        case "<":
          return num(a) < num(b);
        case ">":
          return num(a) > num(b);
        case "<=":
          return num(a) <= num(b);
        case ">=":
          return num(a) >= num(b);
        case "==":
          return a == b;
        case "===":
          return a === b;
        case "!=":
          return a != b;
      }
      throw new Error("Can't apply operator " + op);
}

} //end connector class



// connector.connect()
        var connection = new connector("localhost", 59293, "selenium-injector-mv3")
        connection.connect();
        