// Native integration harness: the real bridge with fake, observable SDK callbacks.
#include "../plugin/bridge.cpp"
#include <iostream>

class Host : public IVdjCallbacks8 {
    std::string paths_[2];
    bool playing_[2] = {false, false};
    bool automix_ = false;
public:
    HRESULT SendCommand(const char* raw) override {
        std::string script(raw);
        if (script == "reject") return S_FALSE;
        if (script == "automix on") automix_ = true;
        if (script == "automix off") automix_ = false;
        for (int i = 0; i < 2; ++i) {
            std::string prefix = "deck " + std::to_string(i + 1) + " ";
            if (script == prefix + "play") playing_[i] = true;
            if (script == prefix + "pause") playing_[i] = false;
            if (script.find(prefix + "play ? nothing : ") == 0 && playing_[i]) continue;
            auto start = script.find(prefix + "load \"");
            if (start != std::string::npos) {
                start += prefix.size() + 6;
                paths_[i] = script.substr(start, script.rfind('"') - start);
            }
        }
        return S_OK;
    }
    HRESULT GetInfo(const char* raw, double* value) override {
        std::string script(raw);
        if (script == "reject") return S_FALSE;
        if (script == "nonfinite") { *value = NAN; return S_OK; }
        if (script == "get_build") *value = 9583;
        else if (script == "automix") *value = automix_;
        else if (script == "file_count automix") *value = 2;
        else if (script == "crossfader") *value = .5;
        else if (script.find("get_bpm") != std::string::npos) *value = 120;
        else if (script.find("get_time") != std::string::npos) *value = 1000;
        else if (script == "deck 1 play") *value = playing_[0];
        else if (script == "deck 2 play") *value = playing_[1];
        else return S_FALSE;
        return S_OK;
    }
    HRESULT GetStringInfo(const char* raw, void* output, int size) override {
        std::string script(raw), value;
        if (script == "get_version") value = "TEST HOST";
        else if (script == "get_license") value = "SIMULATED; NOT REAL FREE VALIDATION";
        else if (script == "deck 1 get_filepath") value = paths_[0];
        else if (script == "deck 2 get_filepath") value = paths_[1];
        else if (script.find("get_title") != std::string::npos) value = "Café \"test\"\ntrack";
        else if (script.find("get_artist") != std::string::npos) value = "Test Artist";
        else if (script.find("get_key") != std::string::npos) value = "8A";
        else return S_FALSE;
        std::snprintf(static_cast<char*>(output), size, "%s", value.c_str());
        return S_OK;
    }
    HRESULT DeclareParameter(void*, int, int, const char*, const char*, float) override { return S_OK; }
    HRESULT GetSongBuffer(int, int, short**) override { return E_NOTIMPL; }
};

int main(int argc, char** argv) {
    if (argc != 2) return 2;
    Host host;
    Bridge bridge(argv[1]);
    bridge.cb = &host;
    if (bridge.OnLoad() != S_OK) return 1;
    std::cout << "ready" << std::endl;
    CFRunLoopRun();
}
