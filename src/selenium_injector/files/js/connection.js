class DefaultDict {
  constructor(defaultVal) {
    return new Proxy({}, {
      get: (target, name) => name in target ? target[name] : defaultVal
    })
  }
}

class handler {
    constructor(connector, request,debug=false){

        this.not_return = false
        this.status = 200
        this.max_depht = 2
        this.event_id = undefined
        this.connector = connector
        this.debug = debug
        var error = undefined
        var result = undefined

        // protocol
        // fist 32 chars is request_id, rest is message
        this.req_id = request.slice(0, 32)
        request = request.slice(32)

        try{ // process request
            var request = JSON.parse(request)

            if(this.debug){
                var debug_msg = {}
                debug_msg[this.req_id] = request
                console.log("request",debug_msg)
            };

            if (request.hasOwnProperty("not_return")){this.not_return = request["not_return"]}
            if (request.hasOwnProperty("max_depth")){this.max_depth = request["max_depth"]}

            var result = this.eval(request)

            if(this.not_return && result && result.catch && this.isFunction(result.catch)){
                    // handle async errors
                    result.catch((e) => {
                        result={"message":e.message,"stack":e.stack};
                        this.status="error"
                    })
                }
            }
        catch(e){
            // handle sync errors
            var result={"message":e.message,"stack":e.stack};
            this.status="error"
            };
        if(!(this.not_return) || this.status === "error"){
            this.send_back(result)
        }
    }
parse(results, status){
    var date = new Date()
    date = date.toLocaleString()
    return '{"result":'+this.stringify(results,0, this.max_depth)+', "status":'+JSON.stringify(status)+',"t":"'+date+'"}'
    }

send_back(...results) {
    var resp_id = this.req_id

    try{var response = this.parse(results, this.status)}
    // serialisation failed
    catch(e){var response = this.parse([{"message":e.message,"stack":e.stack}], "error")}


    if(this.debug){
        var debug_msg = {}
        var type = "response"
        if(resp_id[0] === "E"){type = "event"}
        debug_msg[resp_id] = JSON.parse(response)
        console.log("event",debug_msg)
    };

    // protocol
    // fist 32 chars is request_id, rest is message
    response = resp_id + response
    this.connector.socket.send(response)
}
event_callback(...results){
    this.req_id = this.event_id
    if(this.event_id && this.event_id[0] === "E"){this.send_back(...results)}
    else{throw new TypeError('event_id isn\'t set or doesn\'t start with "E"')}
}
set_event_id(event_id){
 if(event_id[0] === "E"){this.event_id = event_id}
 else{throw new TypeError('event_id[0] needs to equal "E", but got: '+event_id)}
}

// structs

isFunction(functionToCheck) {
 return functionToCheck && {}.toString.call(functionToCheck) === '[object Function]';
}

// eval
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
        case "!":
            var result = !(this.eval(type_json["obj"]))
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
    }.bind(this));
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

stringify(object, depth=0, max_depth=2) {
    function valid(value){
        return !(typeof value === "function" || value == undefined || value == null || value === "")
    }

    // change max_depth to see more levels, for a touch event, 2 is good
    if (depth > max_depth)
        return 'Object';

    var obj = undefined
    if(Array.isArray(object)){
        obj = []
        object.forEach(function (item, index) {
          if(item instanceof Object){item = this.stringify(item, depth+1, max_depth)}
          if(valid(item)){obj.push(item)}
        }.bind(this));
    }
    else{
        obj = {};
        for (let key in object) {
            let value = object[key];
            if (value instanceof globalThis.constructor)
                value = globalThis.constructor.name;
            else if (value instanceof Object)
                value = this.stringify(value, depth+1, max_depth);

            if(valid(value)){obj[key] = value;}
        }
    }

    return depth? obj: JSON.stringify(obj);
}

op(op, a, b) {
      switch (op) {
        case "+":
          return a + b;
        case "-":
          return a - b;
        case "*":
          return a * b;
        case "/":
          return a / b;
        case "^":
          return a ^ b;
        case "%":
          return a % b;
        case "&":
          return a & b;
        case "&&":
          return a && b;
        case "||":
          return a || b;
        case "|":
          return a | b;
        case "<":
          return a < b;
        case ">":
          return a > b;
        case "<=":
          return a <= b;
        case ">=":
          return a >= b;
        case "==":
          return a == b;
        case "===":
          return a === b;
        case "!=":
          return a != b;
        case "=":
          return a = b;
      }
      throw new Error("Can't apply operator " + op);
    }
}

class connector {
  constructor(host, port, username, handler, debug=false) {
    this.host = host;
    this.port = port;
    this.username = username;
    this.handler = handler
    this.debug = debug
    this.connect()
  }

// connection to python
connect(){
    this.socket = new WebSocket("ws://"+this.host+":"+parseInt(this.port));
      this.socket.addEventListener("open", (event) => {
        this.socket.send(this.username);
        this.socket.addEventListener("message", (event) => {
            var handler = new this.handler(this, event.data, this.debug)
            });
        });
      this.socket.addEventListener("error", (event) => {this.connect()});
      this.socket.addEventListener("close", (event) => {this.connect()});
}

} //end connector class