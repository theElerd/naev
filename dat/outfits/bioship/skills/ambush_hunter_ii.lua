notactive = true

function onstealth( p, _po, stealthed )
   if mem.stealthed and not stealthed then
      p:effectAdd( "Ambush Hunter II" )
   end
   mem.stealthed = stealthed
end

function init( p, _po )
   mem.stealthed = p:flags("stealth")
end

function land(p, _po)
   -- At least, ship properties lose the effect bonus.
   -- Still, the icon remains.
   p:effectRm( "Ambush Hunter II" )
end

