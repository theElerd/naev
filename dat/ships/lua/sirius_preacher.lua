local flow = require "ships.lua.lib.flow"
local fmt = require "format"
require "ships.lua.sirius"

local MAXBONUS = 80  -- Maximum value of the bonus
local MINFLOW  = 80  -- Flow required to start getting a bonus
local OVERFLOW = 10  -- How much bonus is needed for an increment
local INCBONUS = 4   -- Increment per OVERFLOW
local BONUS    = INCBONUS / OVERFLOW

function descextra( _p, _s )
   return "#y"..fmt.f(_("For each {over} flow above {min} flow, increases shield regeneration rate by {inc}% up to {max}%."),
      {over=OVERFLOW, min=MINFLOW, inc=INCBONUS, max=MAXBONUS}).."#0"
end

function update( p, _dt )
   local f = flow.get( p, mem )
   local mod = math.min( MAXBONUS, math.max( (f-MINFLOW)*BONUS, 0 ) )
   p:shippropSet{
      shield_regen_mod = mod,
   }
end
