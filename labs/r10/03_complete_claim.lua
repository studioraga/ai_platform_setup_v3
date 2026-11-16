-- KEYS[1] = idempotency key
-- ARGV[1] = current owner token
-- ARGV[2] = completion result identifier
-- ARGV[3] = completed-record TTL milliseconds

local ttl = tonumber(ARGV[3])

if not ttl or ttl < 1000 then
    return redis.error_reply("Invalid completion TTL")
end

local current = redis.call("GET", KEYS[1])

if not current then
    return -1
end

if current ~= ARGV[1] then
    return 0
end

redis.call(
    "SET",
    KEYS[1],
    "completed:" .. ARGV[2],
    "PX",
    ttl
)

return 1
