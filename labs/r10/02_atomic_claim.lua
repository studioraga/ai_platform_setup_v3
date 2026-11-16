-- KEYS[1] = unique idempotency key
-- ARGV[1] = TTL in milliseconds
-- ARGV[2] = claim token

local ttl = tonumber(ARGV[1])

if not ttl or ttl <= 0 then
    return redis.error_reply("Invalid TTL")
end

if not ARGV[2] or ARGV[2] == "" then
    return redis.error_reply("Missing claim token")
end

local result = redis.call(
    "SET", KEYS[1], ARGV[2], "NX", "PX", ttl
)

if result then
    return 1
end

return 0
