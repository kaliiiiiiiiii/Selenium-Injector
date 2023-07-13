
globalThis.returner = function(type_json, debug=false, max_depth=2){
    class handler {
        constructor(max_depth=2, debug=false){
            this.max_depth = max_depth
            this.debug = debug
        }
    CSSSelector(el) {
      if (el.tagName.toLowerCase() == "html")
          return "HTML";
      var str = el.tagName;
      str += (el.id != "") ? "#" + el.id : "";
      if (el.className) {
          var classes = el.className.split(/\s/);
          for (var i = 0; i < classes.length; i++) {
              str += "." + classes[i]
          }
      }
      return this.CSSSelector(el.parentNode) + " > " + str;
}
    handle(request){
            try{ // process request
                if(this.debug){
                    console.log("request",request)
                };
                var result = this.eval(request)
                }
            catch(e){
                // handle sync errors
                var result = result={"message":e.message,"stack":e.stack};
                return this.parse([result], "error")
                };
            if(result && result.constructor && result.constructor == Promise){
                var parse = function(results, status=200){
                    var res = results[0].then(function(result){return this.parse([result])}.bind(this))
                    return res}.bind(this)
                }
            else{var parse = this.parse}
            result = parse.bind(this)([result])
            if(this.debug){
                    console.log("response",result)
                };
            return result
        }
    parse(results, status=200){
        var date = new Date()
        date = date.toLocaleString()
        try{var parsed = {"result":this.stringify(results,0, this.max_depth), "status":status,"t":date}}
        catch(e){var parsed = this.parse([{"message":e.message,"stack":e.stack}], "error")}
        return  parsed
        }
    // structs

    isFunction(functionToCheck) {
     return functionToCheck && {}.toString.call(functionToCheck) === '[object Function]';
    }

    // eval
    eval(type_json){
        class DefaultDict {
          constructor(defaultVal) {
            return new Proxy({}, {
              get: (target, name) => name in target ? target[name] : defaultVal
            })
          }
        }
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
        if(typeof path === "number"){return obj[path]}
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
            var result = res_func(...res_args)
            return result
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
        const valid = function(value){
            // filter out certain values
            return !(value == undefined || value == null || typeof value == "function" || value === "")
        }.bind(this)

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
                    value = globalThis.constructor.name; // handle recursive
                else if (value instanceof Object)
                    value = this.stringify(value, depth+1, max_depth);

                if(valid(value)){obj[key] = value;}
            }
        }

        return depth? obj: obj;
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
    handler = new handler(max_depth, debug)
    return handler.handle(type_json)
}

/*
chrome.scripting.executeScript({
    target:{"tabId":849150942},
    func:returner,
    args:[{"type":"path","path":"navigator"}]
})
*/
