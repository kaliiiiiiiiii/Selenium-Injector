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
proxy.credentials = {}

proxy.set = function(config, patch_webrtc = true, patch_location=true){
    proxy.config = config
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


