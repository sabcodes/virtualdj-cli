#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iomanip>
#include <locale>
#include <sstream>
#include <string>
#include <unistd.h>
#include "vdjPlugin8.h"

namespace {
constexpr size_t MaxRequest = 16384;
void trace(const char* message) {
    const char* home = std::getenv("HOME");
    if (!home) return;
    std::string path = std::string(home) + "/Library/Caches/virtualdj-cli/bridge.log";
    if (FILE* log = std::fopen(path.c_str(), "a")) {
        std::fprintf(log, "pid=%d %s\n", getpid(), message);
        std::fclose(log);
    }
}
std::string portName() {
    return "com.sabcodes.virtualdj-cli." + std::to_string(getuid());
}
std::string jsonString(const std::string& value) {
    std::ostringstream out;
    out << '"';
    for (unsigned char c : value) {
        if (c == '"' || c == '\\') out << '\\' << c;
        else if (c < 32) out << "\\u" << std::hex << std::setw(4) << std::setfill('0') << int(c);
        else out << c;
    }
    out << '"';
    return out.str();
}
std::string error(const std::string& message) {
    return "{\"ok\":false,\"error\":" + jsonString(message) + "}";
}
} // namespace

class Bridge : public IVdjPlugin8 {
public:
    explicit Bridge(std::string name = portName()) : name_(std::move(name)) {}
    ~Bridge() override {
        if (source_) {
            CFRunLoopRemoveSource(CFRunLoopGetMain(), source_, kCFRunLoopCommonModes);
            CFRelease(source_);
        }
        if (port_) {
            if (ownsPort_) CFMessagePortInvalidate(port_);
            CFRelease(port_);
        }
    }
    HRESULT VDJ_API OnGetPluginInfo(TVdjPluginInfo8* info) override {
        trace("metadata requested");
        info->PluginName = "Agent CLI Bridge";
        info->Author = "sabcodes";
        info->Description = "Local VDJScript command and query bridge (feasibility prototype)";
        info->Version = "0.1.0";
        info->Flags = 0;
        info->Bitmap = nullptr;
        return S_OK;
    }
    HRESULT VDJ_API OnGetUserInterface(TVdjPluginInterface8* interface) override {
        interface->Type = VDJINTERFACE_DEFAULT;
        return S_OK;
    }
    HRESULT VDJ_API OnLoad() override {
        trace("OnLoad called");
        if (!cb || port_) { trace("callbacks unavailable or already loaded"); return E_NOTIMPL; }
        CFStringRef name = CFStringCreateWithCString(nullptr, name_.c_str(), kCFStringEncodingUTF8);
        if (!name) return E_NOTIMPL;
        CFMessagePortContext context = {0, this, nullptr, nullptr, nullptr};
        Boolean unusedContext = false;
        port_ = CFMessagePortCreateLocal(nullptr, name, receive, &context, &unusedContext);
        CFRelease(name);
        if (!port_ || unusedContext) { trace("message port registration failed"); return E_NOTIMPL; }
        ownsPort_ = true;
        source_ = CFMessagePortCreateRunLoopSource(nullptr, port_, 0);
        if (!source_) return E_NOTIMPL;
        // Host callbacks execute on the main event loop, never a socket/audio worker.
        CFRunLoopAddSource(CFRunLoopGetMain(), source_, kCFRunLoopCommonModes);
        CFRunLoopWakeUp(CFRunLoopGetMain());
        trace("message port ready");
        return S_OK;
    }
    ULONG VDJ_API Release() override { delete this; return 0; }

private:
    std::string name_;
    CFMessagePortRef port_ = nullptr;
    CFRunLoopSourceRef source_ = nullptr;
    bool ownsPort_ = false;

    std::string dispatch(SInt32 operation, CFDataRef data) {
        if (!data || CFDataGetLength(data) <= 0 || size_t(CFDataGetLength(data)) > MaxRequest)
            return error("invalid_request_size");
        std::string input(reinterpret_cast<const char*>(CFDataGetBytePtr(data)), CFDataGetLength(data));
        auto separator = input.find('\n');
        if (separator == std::string::npos) return error("invalid_request");
        std::istringstream clock(input.substr(0, separator));
        clock.imbue(std::locale::classic());
        double deadline = 0;
        clock >> deadline;
        if (!clock || !clock.eof() || !std::isfinite(deadline)) return error("invalid_deadline");
        if (CFAbsoluteTimeGetCurrent() + 978307200.0 > deadline) return error("request_expired");
        std::string script = input.substr(separator + 1);
        if (script.empty() || script.find_first_of("\r\n\t") != std::string::npos ||
            script.find('\0') != std::string::npos) return error("invalid_script");
        CFStringRef utf8 = CFStringCreateWithBytes(nullptr,
            reinterpret_cast<const UInt8*>(script.data()), script.size(), kCFStringEncodingUTF8, false);
        if (!utf8) return error("invalid_utf8");
        CFRelease(utf8);
        if (!cb) return error("host_callbacks_unavailable");
        HRESULT result;
        std::string value;
        switch (operation) {
            case 1:
                result = SendCommand(script.c_str());
                value = "true";
                break;
            case 2: {
                double number = 0;
                result = GetInfo(script.c_str(), &number);
                if (!std::isfinite(number)) return error("nonfinite_query_result");
                std::ostringstream out;
                out.imbue(std::locale::classic());
                out << std::setprecision(17) << number;
                value = out.str();
                break;
            }
            case 3: {
                char text[65536] = {};
                result = GetStringInfo(script.c_str(), text, sizeof(text));
                text[sizeof(text) - 1] = '\0';
                value = jsonString(text);
                break;
            }
            default: return error("unknown_operation");
        }
        if (result != S_OK)
            return "{\"ok\":false,\"error\":\"sdk_rejected\",\"hresult\":" + std::to_string(result) + "}";
        return "{\"ok\":true,\"value\":" + value + "}";
    }
    static CFDataRef receive(CFMessagePortRef, SInt32 operation, CFDataRef data, void* context) {
        std::string response;
        try { response = static_cast<Bridge*>(context)->dispatch(operation, data); }
        catch (...) { response = error("invalid_request_or_callback_exception"); }
        return CFDataCreate(nullptr, reinterpret_cast<const UInt8*>(response.data()), response.size());
    }
};

HRESULT VDJ_API DllGetClassObject(const GUID& clsid, const GUID& iid, void** object) {
    if (!object) return E_NOTIMPL;
    *object = nullptr;
    if (std::memcmp(&clsid, &CLSID_VdjPlugin8, sizeof(GUID)) != 0 ||
        std::memcmp(&iid, &IID_IVdjPluginBasic8, sizeof(GUID)) != 0)
        { trace("unsupported SDK interface"); return CLASS_E_CLASSNOTAVAILABLE; }
    trace("basic plugin instance requested");
    try { *object = new Bridge(); return S_OK; }
    catch (...) { return E_NOTIMPL; }
}
