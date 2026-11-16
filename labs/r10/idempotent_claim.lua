-- Redis RESEARCH-ONLY atomic claim. KEYS[1] namespace/key; ARGV[1] TTL milliseconds.
-- Return 1 for first claim and 0 for duplicate. No exactly-once execution claim.
local ttl = tonumber(ARGV[1])
if not ttl or ttl < 1000 then return redis.error_reply('invalid_ttl') end
if redis.call('SET', KEYS[1], 'claimed', 'NX', 'PX', ttl) then return 1 end
return 0
