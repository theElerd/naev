--[[
<?xml version='1.0' encoding='utf8'?>
<mission name="Commodity Run">
 <avail>
  <priority>5</priority>
  <cond>var.peek("commodity_runs_active") == nil or var.peek("commodity_runs_active") &lt; 3</cond>
  <chance>90</chance>
  <location>Computer</location>
  <faction>Dvaered</faction>
  <faction>Empire</faction>
  <faction>Frontier</faction>
  <faction>Goddard</faction>
  <faction>Independent</faction>
  <faction>Proteron</faction>
  <faction>Sirius</faction>
  <faction>Soromid</faction>
  <faction>Thurion</faction>
  <faction>Traders Guild</faction>
  <faction>Za'lek</faction>
 </avail>
 <notes>
  <tier>1</tier>
 </notes>
</mission>
--]]
--[[
   Commodity delivery missions.
--]]
local pir = require "common.pirate"
local fmt = require "format"
local vntk = require "vntk"

--Mission Details
misn_title = _("{cargo} Delivery")
misn_desc = _("{pnt} has an insufficient supply of {cargo} to satisfy the current demand. Go to any planet which sells this commodity and bring as much of it back as possible.")

cargo_land = {}
cargo_land[1] = _("The containers of {cargo} are carried out of your ship and tallied. After several different men double-check the register to confirm the amount, you are paid {credits} and summarily dismissed.")
cargo_land[2] = _("The containers of {cargo} are quickly and efficiently unloaded, labeled, and readied for distribution. The delivery manager thanks you with a credit chip worth {credits}.")
cargo_land[3] = _("The containers of {cargo} are unloaded from your vessel by a team of dockworkers who are in no rush to finish, eventually delivering {credits} after the number of tonnes is determined.")
cargo_land[4] = _("The containers of {cargo} are unloaded by robotic drones that scan and tally the contents. The human overseer hands you {credits} when they finish.")

osd_title = _("Commodity Delivery")
paying_faction = faction.get("Independent")


-- A script may require "missions/neutral/commodity_run" and override this
-- with a table of (raw) commodity names to choose from.
commchoices = nil


function update_active_runs( change )
   local current_runs = var.peek( "commodity_runs_active" )
   if current_runs == nil then current_runs = 0 end
   var.push( "commodity_runs_active", math.max( 0, current_runs + change ) )

   -- Note: This causes a delay (defined in create()) after accepting,
   -- completing, or aborting a commodity run mission. This is
   -- intentional.
   var.push( "last_commodity_run", time.tonumber( time.get() ) )
end


function create ()
   -- Note: this mission does not make any system claims.
   misplanet, missys = planet.cur()

   if commchoices == nil then
      local std = commodity.getStandard();
      chosen_comm = std[rnd.rnd(1, #std)]:nameRaw()
   else
      chosen_comm = commchoices[rnd.rnd(1, #commchoices)]
   end
   local comm = commodity.get(chosen_comm)
   local mult = 1 + math.abs(rnd.twosigma() * 2)
   price = comm:price() * mult

   local last_run = var.peek( "last_commodity_run" )
   if last_run ~= nil then
      local delay = time.create(0, 7, 0)
      if time.get() < time.fromnumber(last_run) + delay then
         misn.finish(false)
      end
   end

   for _i, j in ipairs( missys:planets() ) do
      for _k, v in pairs( j:commoditiesSold() ) do
         if v == comm then
            misn.finish(false)
         end
      end
   end

   -- Set Mission Details
   misn.setTitle( fmt.f( misn_title, {cargo=comm} ) )
   misn.markerAdd( system.cur(), "computer" )
   misn.setDesc( fmt.f( misn_desc, {pnt=misplanet, cargo=comm} ) )
   misn.setReward( fmt.f(_("{credits} per tonne"), {credits=fmt.credits(price)} ) )
end


function accept ()
   local comm = commodity.get(chosen_comm)

   misn.accept()
   update_active_runs( 1 )

   misn.osdCreate(osd_title, {
      fmt.f(_("Buy as much {cargo} as possible"), {cargo=comm} ),
      fmt.f(_("Take the {cargo} to {pnt} in the {sys} system"), {cargo=comm, pnt=misplanet, sys=missys} ),
   })

   hook.enter("enter")
   hook.land("land")
end


function enter ()
   if pilot.cargoHas( player.pilot(), chosen_comm ) > 0 then
      misn.osdActive(2)
   else
      misn.osdActive(1)
   end
end


function land ()
   local amount = pilot.cargoHas( player.pilot(), chosen_comm )
   local reward = amount * price

   if planet.cur() == misplanet and amount > 0 then
      local txt = fmt.f(cargo_land[rnd.rnd(1, #cargo_land)],
            {cargo=_(chosen_comm), credits=fmt.credits(reward)} )
      vntk.msg(_("Delivery success!"), txt)
      pilot.cargoRm(player.pilot(), chosen_comm, amount)
      player.pay(reward)
      if not pir.factionIsPirate( paying_faction ) then
         pir.reputationNormalMission(rnd.rnd(2,3))
      end
      update_active_runs(-1)
      misn.finish(true)
   end
end


function abort ()
   update_active_runs(-1)
end

