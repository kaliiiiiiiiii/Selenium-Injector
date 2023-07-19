

// chrome extension libs

globalThis.proxy = {}
proxy.credentials = {}

proxy.set = function(config, patch_webrtc = true, patch_location=true){
    proxy.config = config
    chrome.proxy.settings.set({value: proxy.config, scope: "regular"}, function() {});
    if (patch_webrtc){webrtc_leak.disable();};
    if(patch_location){contentsettings.set_location("block")}
}

proxy.get = function(callback){
    chrome.proxy.settings.get({'incognito': false}, callback);
}

proxy.clear = function(clear_webrtc=true, clear_location=true){
    chrome.proxy.settings.clear({});
    if(clear_webrtc){webrtc_leak.clear();}
    if (clear_location){contentsettings.set_location("allow")}
    delete(proxy.config)
}


proxy.set_auth = function(username, password, urls=["<all_urls>"]){
    proxy.credentials = {"password":password, "username":username, "urls":urls};

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
   proxy.credentials = {};
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

globalThis.scripting = {}

scripting.mv3_eval_str = function(code, target){
    chrome.scripting.executeScript({
    target: target,
    func: code => {
      const el = document.createElement('script');
      el.textContent = code;
      document.documentElement.appendChild(el);
      el.remove();
    },
    args: [code],
    world: 'MAIN',
    //injectImmediately: true, // Chrome 102+
  });
}

scripting.tab_exec = function(callback, type_dict, tab_id, max_depth, debug){
        if(chrome.scripting){ //mv3
            chrome.scripting.executeScript({
                target:{"tabId":tab_id},
                func:globalThis.returner,
                args:[type_dict, debug, max_depth]}).then((result) => {callback(result[0]["result"])})
        }
        else{ // mv2, uses Function.prototype.toString()
            chrome.tabs.executeScript(tab_id,
                {"code":`(${globalThis.returner.toString()})(${JSON.stringify(type_dict)},${JSON.stringify(debug)},${JSON.stringify(max_depth)})`},
                (result) => {callback(result[0])})
        }

    }

globalThis.tab_event = {checked_tabs:[],tab_callbacks:undefined}

tab_event.req_callback = function(details) {
    var tab_id = details['tabId']
    if(tab_id >= 0){
        if(!(tab_event.checked_tabs.includes(tab_id))){
            tab_event.tab_callbacks.forEach((func) => {
                func(details)
            })
            tab_event.checked_tabs.push(tab_id)
        }
    }
    return {};
  }

tab_event.on_tab_removed = function(tabId) {
    var idx= tab_event.checked_tabs.indexOf(tabId);
    tab_event.checked_tabs = tab_event.checked_tabs.splice(idx, 1);
}

tab_event.addEventListener = function(callback){
    if(!(tab_event.tab_callbacks)){
        tab_event.tab_callbacks = [callback]
        chrome.webRequest.onBeforeRequest.addListener(
          tab_event.req_callback,
          {urls: ["<all_urls>"]},
          ["blocking"]
        );
        chrome.tabs.onRemoved.addListener(tab_event.on_tab_removed)
    }else{tab_event.tab_callbacks.push(callback)}
}

tab_event.removeEventListener = function(listener){
    var idx= tab_event.tab_callbacks.indexOf(listener);
    tab_event.tab_callbacks = tab_event.tab_callbacks.splice(idx, 1);
}

tab_event.continue_if_paused = function(tab_id){
}
tab_event.pause = function(tab_id){

}



