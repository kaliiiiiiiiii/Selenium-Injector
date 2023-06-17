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

// structs

class DefaultDict {
  constructor(defaultVal) {
    return new Proxy({}, {
      get: (target, name) => name in target ? target[name] : defaultVal
    })
  }
}

function isFunction(functionToCheck) {
 return functionToCheck && {}.toString.call(functionToCheck) === '[object Function]';
}


// connection to python
globalThis.connection = {}
connection.host = "localhost"
connection.port = 8001
connection.username = "selenium_injector-mv3"

connection.connect= function(){
    connection.socket = new WebSocket("ws://"+connection.host+":"+parseInt(connection.port));
      connection.socket.addEventListener("open", (event) => {
        connection.socket.send(connection.username);
        connection.socket.addEventListener("message", (event) => {
            connection.handler(event.data)
            });
        });
      connection.socket.addEventListener("error", (event) => {connection.connect()});
      connection.socket.addEventListener("close", (event) => {connection.connect()});
    };

connection.send_back = function(...results){
    var response = '{"result":'+types.stringify(results)+', "status":'+JSON.stringify(types.status)+'}';
    console.log({"response":JSON.parse(response)});
    connection.socket.send(response)
}

connection.handler = function(request){
        var request = JSON.parse(request);
        console.log({"request":request})
        connection.not_return = request["not_return"]
        types.status = 200
        try{var result = types.eval(request)}catch(e){
            var result={"message":e.message,"stack":e.stack};
            types.status="error"};
        if(!(connection.not_return)){connection.send_back(result)}
    }

// parser for unsafe-eval bypass
globalThis.types = {};

types.eval = function(type_json){
    var defaultdict = new DefaultDict(undefined)
    var type_json = Object.assign({}, defaultdict, type_json)
    var type = type_json["type"];
    switch (type) {
        case "type":
            var result = types.eval(type_json["type_json"]);
            break;
        case "path":
            var result = types.path(type_json["path"], type_json["obj"]);
            break;
        case "exec":
            var result = types.exec(type_json["func"], type_json["args"]);
            break;
        case "val":
            var result = type_json["val"];
            break;
        case "if":
            var result = types.if_else(type_json["if"],type_json["do"],type_json["else"]);
            break;
        case "list":
            var result = types.list(type_json["list"]);
            break;
        case "dict":
            var result = types.dict(type_json["dict_list"]);
            break;
        case "op":
            var result = types.op(type_json["op"], types.eval(type_json["a"]), types.eval(type_json["b"]));
            break;
        default:
            reportError(TypeError("Expected type_json, but got "+types.stringify(type_json)));
    }
    return result;
}

types.path = function(path, obj = undefined){
    if (obj == undefined){obj = globalThis}
    for (var i=0, path=path.split('.'), len=path.length; i<len; i++){
        obj = obj[path[i]];
    };
    return obj;
};

types.exec = function(func, args=[]){
    var res_args = [];
    args.forEach(function (item, index) {
        res_args.push(types.eval(item))
    });
    var res_func = types.eval(func)
    if (isFunction(res_func)){
        res_func(...res_args)
    }
    else{
        throw TypeError("Expected a function, got "+types.stringify(res_func))
    };
};

types.list = function(list){
    var results = [];
    list.forEach(function(item, index){
        results.push(types.eval(item))
    });
    return results
};

types.dict = function(dict_list){
    var res_dict = {};
    dict_list.forEach(function(item) {
        res_dict[types.eval(item["key"])] = types.eval(item["val"])
    });
    return res_dict
};

types.if_else = function(condition, statement, else_statement=undefined){
    if (types.eval(condition)){
        var result = types.eval(statement)
    }
    else {
        if (else_statement == undefined){
            var result = undefined
        }
        else {
            var result = types.eval(else_statement)
        }
    };
    return result
};

types.stringify = function(obj){
    var result = JSON.stringify(obj, types.replacer)
    return result
};

types.replacer = function replacer(key, value) {
  // Filtering out properties
  if (isFunction(value)) {
    types.status = "func_to_str"
    return value.toLocaleString();
  }
  else if (value == undefined){
    return null
  }
  else {
    return value
  }
};

types.op = function apply_op(op, a, b) {
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
      switch (op) {
        case "+":
          return num(a) + num(b);
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
        case "!=":
          return a != b;
      }
      throw new Error("Can't apply operator " + op);
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
    chrome.proxy.settings.get({'incognito': false}, connection.send_back);
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

