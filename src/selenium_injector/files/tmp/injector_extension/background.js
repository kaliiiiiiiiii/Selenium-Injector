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
connection = {}
connection.host = "localhost"
connection.port = 8001
connection.username = "selenium_injector"

connection.connect= function(){
    connection.socket = new WebSocket("ws://"+connection.host+":"+parseInt(connection.port));
      connection.socket.addEventListener("open", (event) => {
        connection.socket.send(connection.username);
        connection.socket.addEventListener("message", (event) => {
            connection.socket.send(connection.handler(event.data))
            });
        });
      connection.socket.addEventListener("error", (event) => {connection.connect()});
      connection.socket.addEventListener("close", (event) => {connection.connect()});
    };

connection.handler = function(request){
        request = JSON.parse(request);
        types.status = 200
        try{result = types.eval(request)}catch(e){
            result={"message":e.message,"stack":e.stack};
            types.status="error"};
        response = '{"result":'+types.stringify(result)+', "status":'+JSON.stringify(types.status)+'}';
        console.log({"request":request, "response":JSON.parse(response)});
        return response;
    }


// perser for unsafe-eval bypass
types = {}

types.eval = function(type_json){
    var defaultdict = new DefaultDict(undefined)
    type_json = Object.assign({}, defaultdict, type_json)
    var type = type_json["type"];
    if (type == "type"){var result = types.eval(type_json["type_json"])}
    else if (type == "path"){var result = types.path(type_json["path"], type_json["obj"])}
    else if (type == "exec"){var result = types.exec(type_json["func"], type_json["args"])}
    else if (type == "val"){var result = type_json["val"]}
    else if (type == "not"){var result = types.not(type_json["type_json"])}
    else if (type == "if"){var result = types.if_else(type_json["if"],type_json["do"],type_json["else"])}
    else if (type == "list"){var result = types.list(type_json["list"])}
    else if (type == "dict"){var result = types.dict(type_json["dict_list"])}
    else {reportError(TypeError("Expected type_json, but got "+types.stringify(type_json)))}
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
    res_args = [];
    args.forEach(function (item, index) {
        res_args.push(types.eval(item))
    });
    res_func = types.eval(func)
    if (isFunction(res_func)){
        res_func(...res_args)
    }
    else{reportError(TypeError("Expected a function, got "+types.stringify(res_func)))};
}

types.list = function(list){
    var results = [];
    list.forEach(function(item, index){results.push(types.eval(item))});
    return results
}

types.dict = function(dict_list){
    res_dict = {};
    dict_list.forEach(function(item) {
        res_dict[types.eval(item["key"])] = types.eval(item["val"])
    });
    return res_dict
}

types.not = function(type_json){
    return !(types.eval(type_json))
}

types.if_else = function(condition, statement, else_statement=undefined){
    if (types.eval(condition)){result = types.eval(statement)}
    else {
        if (else_statement == undefined){result = undefined}
        else {result = types.eval(else_statement)}
    };
    return result
}

types.stringify = function(obj){
    var result = JSON.stringify(obj, types.replacer)
    return result
}

types.replacer = function replacer(key, value) {
  // Filtering out properties
  if (isFunction(value)) {
    types.status = "func_to_str"
    return value.toLocaleString();
  }
  else if (value == undefined){return null}
  else {return value}
}

// chrome extension libs

proxy = {}

proxy.set = function(scheme,host,port, patch_webrtc = true, patch_location=true){
    proxy.config = {
        mode: "fixed_servers",
        rules: {
           singleProxy: {
             scheme: scheme,
             host: host,
             port: port
           },
          bypassList: ["localhost"]
        }
    };
    chrome.proxy.settings.set({value: proxy.config, scope: "regular"}, function() {});
    if (patch_webrtc){webrtc_leak.disable();};
    if(patch_location){contentsettings.set_location("block")}
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

webrtc_leak = {}

webrtc_leak.disable = function(value="disable_non_proxied_udp"){
      // https://github.com/aghorler/WebRTC-Leak-Prevent
      chrome.privacy.network.webRTCIPHandlingPolicy.set({
            "value": value
          });
}

webrtc_leak.clear = function(){
      webrtc_leak.disable("default")
}

contentsettings = {}

contentsettings.set = function(setting,value, urls="<all_urls>"){
    chrome.contentSettings[setting].set({"primaryPattern":urls,"setting":value}, console.log)
}

contentsettings.set_location = function(setting = "ask",urls="<all_urls>"){
    contentsettings.set("location", setting, urls)
}


        connection.user_name = "selenium_injector";
        connection.host = "localhost";
        connection.port = 8001;
        connection.connect();
        