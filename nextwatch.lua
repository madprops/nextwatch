time = 0
path = ""

local opts = {
    watched = os.getenv("HOME") .. "/.config/nextwatch/watched.txt",
    min_seconds = 30,
}

function round(value)
    return value >= 0 and math.floor(value + 0.5) or math.ceil(value - 0.5)
end

function file_exists(path)
    local f = io.open(path, "r")

    if f ~= nil then
        io.close(f)
        return true
    end
end

function makedir(path)
    local dir = path:match("(.*/)")

    if dir then
        os.execute("mkdir -p " .. dir)
    end
end

function file_append(path, content)
    makedir(path)
    local h = assert(io.open(path, "ab"))
    h:write(content)
    h:close()
end

function at_load()
    time = os.time()
    path = mp.get_property("path")
end

function at_shutdown()
    local seconds = round(os.time() - time)

    if seconds > opts.min_seconds then
        if not file_exists(opts.watched) then
            file_append(opts.watched, "")
        end

        local content = io.open(opts.watched):read("*all")
        local found = false

        for line in content:gmatch("[^\r\n]+") do
            if line == path then
                found = true
                break
            end
        end

        if not found then
            file_append(opts.watched, path .. "\n")
        end
    end
end

mp.register_event("file-loaded", at_load)
mp.register_event("shutdown", at_shutdown)