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
        this.connector = connector
        this.debug = debug
        var error = undefined
        var result = undefined

        // protocoll
        // fist 32 chars is request_id, rest is message
        this.req_id = request.slice(0, 32)
        request = request.slice(32)

        try{ // process request
            var request = JSON.parse(request)

            if(this.debug){console.log({"request":request})}

            if (request.hasOwnProperty("not_return")){this.not_return = request["not_return"]}

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
        if(!(this.not_return) || this.status=="error"){
            this.send_back(result)
        }
    }
parse(results, status){return '{"result":'+this.stringify(results)+', "status":'+JSON.stringify(status)+'}'}
send_back(...results) {

    try{var response = this.parse(results, self.status)}
    // serialisation failed
    catch(e){var response = this.parse([{"message":e.message,"stack":e.stack}], "error")}

    if(this.debug){console.log({"response":JSON.parse(response)})
                  };

    // protocoll
    // fist 32 chars is request_id, rest is message
    response = this.req_id + response
    this.connector.socket.send(response)
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