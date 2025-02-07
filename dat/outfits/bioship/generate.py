#!/usr/bin/env python3

import os
import sys
import math
N_ = lambda text: text

# Based on some XML templates and the specs below, we're going to generate families of outfit XML files.
# First things first: what are we supposed to be doing?

class Build:
    ''' By default, build everything in-tree. '''

    def read_template(self, name):
        return open(f'templates/{name}').read()

    def file_names(self, names):
        return [f"{n.lower().replace(' ','_')}.xml" for n in names]

    def open_output(self, names):
        return (open(fn, 'w') for fn in self.file_names(names))

class MesonBuild(Build):
    ''' If Meson invokes generate.py <template path> -o <output paths>, build only the outfit family that matches the command. '''

    def __init__(self, template_path, _, *output_paths):
        self.template_path = template_path
        self.output_paths = output_paths
        self.template_name = os.path.basename(template_path)
        self.output_names = [os.path.basename(p) for p in output_paths]

    def read_template(self, name):
        if name == self.template_name:
            return open(self.template_path).read()

    def open_output(self, names):
        if self.file_names(names) == self.output_names:
            for fn in self.output_paths:
                yield open(fn, 'w')

build = MesonBuild(*sys.argv[1:]) if sys.argv[2:3] == ['-o'] else Build()

# Hopefully we can refactor this once the behavior is finalized and we're unafraid of merge conflicts. Anyway, back to the show.

def lerpt( t ):
    return lambda x: t[int(math.floor(x*(len(t)*0.99999)))]

def lerp( a, b, ta=0.0, tb=1.0 ):
    return lambda x: a + (x-ta) * (b-a) / (tb-ta)

def lerpr( a, b, ta=0.0, tb=1.0 ):
    def f(x):
        res=int(round(lerp(a,b,ta,tb)(x)))
        return 0 if res<0 else res;
    return f

from math import log,exp

# Does geometric interpolation instead of arithmetic interpolation.
def eerp( a, b, ta=0.0, tb=1.0 ):
    return lambda x: exp(lerp(log(a),log(b),ta,tb)(x))

def eerpr( a, b, ta=0.0, tb=1.0 ):
    return lambda x: int(round(eerp(a,b,ta,tb)(x)))

class BioOutfit:
    def __init__( self, template, params ):
        self.template = template
        self.params = params
        self.txt = build.read_template(template)

    def run(self, names):
        files = build.open_output(names)
        for k, (n, f) in enumerate(zip(names, files)):
            x = 1 if len(names)==1 else k/(len(names)-1)
            p = {k: v(x) if callable(v) else v for k, v in self.params.items()}
            p["name"]  = n
            with f:
                txt = self.txt.format(**p)
                txt = txt.replace( "<general>", "<!-- THIS OUTFIT IS AUTOGENERATED. DO NOT EDIT DIRECTLY! -->\n <general>" )
                f.write( txt )

desc = {}
desc["brain"] = N_("The brain is a Soromid bioship's equivalent to core systems in synthetic ships. Possibly the most important organ, the brain provides processing power and allocates energy to the rest of the organism. All brains start off undeveloped, but over time, just like the ships themselves, they grow and improve.")
desc["engine"] = N_("The gene drive is a Soromid bioship's equivalent to engines in synthetic ships. It is charged with moving the organism through space and is even capable of hyperspace travel. All gene drives start off undeveloped, but over time, just like the ships themselves, they grow and improve.")
desc["hull"] = N_("The shell is a Soromid bioship's natural protection, equivalent to hulls of synthetic ships. The shell is responsible both for protecting the organism's internal organs and for creating camouflage to reduce the risk of being detected by hostiles. All shells start off undeveloped, but over time, just like the ships themselves, they grow and improve.")

typename = {}
typename["brain"] = N_("Bioship Brain")
typename["engine"] = N_("Bioship Gene Drive")
typename["hull"] = N_("Bioship Shell")

## BioOutfit generation rules.
## See comments in this directory's meson.build file: these rules must match the build rules.


## Cortex recipe:
##    "absorb":       lerpr(  <Unicorp>-3, <S&K>-3 ),
##    "armour":       lerp(  <Unicorp>, <S&K> )
##    "cargo":        lerpr(   <S&K>, (<S&K>+<Unicorp>)/2 ),
##    "price":        lerpr(   <S&K>/2, <S&K>),
##    "mass":         <S&K>,
##    "armour":       lerp(   <Unicorp>, <S&K> )
##

## Gene Drive recipe:
## Corresponds (when maxed) to some existing engine <ref> mentionned in the comment.
##    "price":        lerpr( <ref>/2.0, <ref> ),
##    "accel":        lerp(  <ref>-15%, <ref> ),
##    "turn":         lerp(  <ref>-15%, <ref> ),
##    "speed":        lerp(  <ref>-15%, <ref> ),
## <ref>-15% are currently really approximate.

## Cerebrum recipe (small):
##    "price":        lerpr(  <orion>, <orion>*2 ),
##    "mass":         lerpr(  <orion>, <orion>*1.25 ),
##    "shield" :      lerp(   <orion>, <orion>*1.25 ),
##    "shield_regen": lerp(   <orion>, <orion>*1.25 ),
##    "energy" :      lerp(   <orion>, <orion>*1.25 ),
##    "energy_regen": lerp(   <orion>, <orion>*1.25 ),

## Cerebrum recipe (medium/large):
##    "price":        <orion>+1/2*(<shield_booster>+<shield capacitor>),
##    "mass":         <orion>+1/2*(<shield_booster>+<shield capacitor>),
##    "shield":       lerp( <orion> , <orion>+1/2*<shield capacitor> ),
##    "shield_regen": lerp( <orion> , <orion>+1/2*<shield_booster> ),
##    "energy" :      lerp(   <orion>, ??? ),
##    "energy_regen": lerp(   <orion>, ??? ),

params=(0.25,0.625)
BioOutfit( "weapon.xml.template", {
    "typename": N_("Bioship Weapon Organ"),
    "size":     "small",
    "mass":     lerpr(   3, 6, *params),
    "price" :   lerpr(   19e3, 45e3 , *params),
    "desc":     N_("The Stinger Organ is able to convert energy into hot plasma that is able to eat easily through shield and armour of opposing ships over time. While not an especially powerful offensive organ, it is prized for its reliability."),
    "gfx_store":lerpt(("organic_plasma_s1.webp", "organic_plasma_s2.webp","organic_plasma_s3.webp")),
    "specific": "bolt",
    "gfx":      "plasma.png",
    "gfx_end":  "plasma2-end.png",
    "sound":    "bioplasma",
    "spfx_shield":"ShiS",
    "spfx_armour":"PlaS",
    "lua":      "bioplasma.lua",
    # -5% delay
    "delay":    eerp(   0.95*1.2,  0.95*1.4, *params),
    "speed" :   700,
    "range" :   eerpr(  700,  800, *params),
    "falloff":  eerpr(  600,  650, *params),
    # -25% energy consumption ( compensation for energy regen loss )
    "energy":   eerpr(6*0.75, 16.5*0.75, *params),
    "trackmin": 0,
    # +20% tracking
    "trackmax": eerpr(0.8*2000,  0.8*3000, *params),
    "penetrate":lerpr(   0,    10, *params),
    "damage":   eerp( 19.5,    27, *params),
    "extra":    "<swivel>22</swivel>",
} ).run( [
    N_("Stinger Organ I"),
    N_("Stinger Organ II"),
    N_("Stinger Organ III"),
] )

# Perleve Cerebrum  =>  Orion_2301
BioOutfit( "cerebrum.xml.template", {
    "typename":     typename["brain"],
    "size":         "small",
    "price":        lerpr(   120e3, 2*120e3 ),
    "mass":         lerpr(14,14*1.25*0.99999),
    "desc":         desc["brain"],
    "gfx_store":    "organic_core_s1.webp",
    "cpu":          lerpr(   5,   8 ),
    "shield" :      lerp(  200, 250 ),
    "shield_regen": lerp(    7,   9 ),
    "energy":       lerp(  200, 250 ),
    "energy_regen": lerp(   10,  13 ), # was 19 (-33%)
} ).run( [
    N_("Perleve Cerebrum I"),
    N_("Perleve Cerebrum II"),
] )

# Perlevis Gene Drive  =>  Tricon Zephyr
BioOutfit( "gene_drive.xml.template", {
    "typename":     typename["engine"],
    "size":         "small",
    "price":        lerpr(   67.5e3, 135e3 ),
    "mass":         10,
    "desc":         desc["engine"],
    "gfx_store":    lerpt(("organic_engine_fast_s1.webp","organic_engine_fast_s2.webp")),
    "accel":        lerp(  165, 195 ),
    "turn":         lerp(  130, 160 ),
    "speed":        lerp(  295, 345 ),
    "fuel":         300,
    "energy_malus": lerp(    4,   4 ),
    "engine_limit": lerp(  140, 140 ),
} ).run( [
    N_("Perlevis Gene Drive I"),
    N_("Perlevis Gene Drive II"),
] )

# Perlevis Cortex  ==>  (1) Unicorp_d2  (2) S&K Ultralight Combat Plating
BioOutfit( "cortex.xml.template", {
    "typename":     typename["hull"],
    "size":         "small",
    "price":        lerpr(   65e3, 130e3 ),
    "mass":         30,
    "desc":         desc["hull"],
    "gfx_store":    "organic_hull_t.webp",
    "cargo":        lerpr(   2, 6 ),
    "absorb":       lerpr(   0, 2 ),
    "armour":       lerp(   50, 70 )
} ).run( [
    N_("Perlevis Cortex I"),
    N_("Perlevis Cortex II"),
] )

# Laevum Cerebrum  =>  Orion_3701
BioOutfit( "cerebrum.xml.template", {
    "typename":     typename["brain"],
    "size":         "small",
    "price":        lerpr(   210e3, 262.5e3 ),
    "mass":         lerpr(75,75*1.25),
    "desc":         desc["brain"],
    "gfx_store":    "organic_core_s2.webp",
    "cpu":          lerpr(  24,  32 ),
    "shield" :      lerp(  250, 312 ), # was 310
    "shield_regen": lerp(    8,  10 ),
    "energy":       lerp(  400, 500 ), # was 400
    "energy_regen": lerp(   21,  26 ), # was 34 (-25%)
} ).run( [
    N_("Laevum Cerebrum I"),
    N_("Laevum Cerebrum II"),
] )

# Laeviter Gene Drive  =>  Tricon Zephyr II 
BioOutfit( "gene_drive.xml.template", {
    "typename":     typename["engine"],
    "size":         "small",
    "price":        lerpr(112.5e3, 225e3 ),
    "mass":         20,
    "desc":         desc["engine"],
    "gfx_store":    lerpt(("organic_engine_fast_s1.webp","organic_engine_fast_s2.webp")),
    "accel":        lerp(  135, 160 ),
    "turn":         lerp(  115, 140 ),
    "speed":        lerp(  240, 290 ),
    "fuel":         400,
    "energy_malus": lerp(   12,  12 ),
    "engine_limit": lerp(  320, 320 ),
} ).run( [
    N_("Laeviter Gene Drive I"),
    N_("Laeviter Gene Drive II"),
] )

# Laevis Gene Drive  =>  Melendez Ox XL 
BioOutfit( "gene_drive_melendez.xml.template", {
    "typename":     typename["engine"],
    "size":         "small",
    "price":        lerpr( 47.5e3, 95e3 ),
    "mass":         25,
    "desc":         desc["engine"],
    "gfx_store":    lerpt(("organic_engine_strong_s1.webp","organic_engine_strong_s2.webp")),
    "accel":        lerp(  100, 115 ),
    "turn":         lerp(   80,  95 ),
    "speed":        lerp(  190, 225 ),
    "fuel":         600,
    "energy_malus": lerp(    7,   7 ),
    "engine_limit": lerp(  420, 420 ),
} ).run( [
    N_("Laevis Gene Drive I"),
    N_("Laevis Gene Drive II"),
] )

BioOutfit( "weapon.xml.template", {
    "typename": N_("Bioship Weapon Organ"),
    "size":     "medium",
    "mass":     16,
    "price" :   lerpr(   0, 20e3 ),
    "desc":     N_("The Talon Organ is an enlarged and more powerful version of the Stinger Organ. Like its smaller counterpart, is able to convert energy into hot plasma that is able to eat easily through shield and armour of opposing ships. The hot plasma is able to cling to ship's shields and hulls dealing continuous damage after impact."),
    "gfx_store":"organic_plasma_l.webp",
    "specific": "bolt",
    "gfx":      "plasma2.png",
    "gfx_end":  "plasma2-end.png",
    "sound":    "bioplasma",
    "spfx_shield":"ShiS",
    "spfx_armour":"PlaS2",
    "lua":      "bioplasma2.lua",
    "delay":    1.4,
    "speed" :   700,
    "range" :   lerp( 1000, 1400 ),
    "falloff":  lerp(  900, 1200 ),
    "energy":   lerp(   46,  58 ),
    "trackmin": lerp( 1500, 2000 ),
    "trackmax": lerp( 4500, 6000 ),
    "penetrate":lerpr(  35,  50 ),
    "damage":   lerp(   35,  47 ),
    "extra":    "<swivel>22</swivel>",
} ).run( [
    N_("Talon Organ I"),
    N_("Talon Organ II"),
    N_("Talon Organ III"),
    N_("Talon Organ IV"),
] )

# Laevis Cortex  =>  (1) Unicorp_d9  (2) S&K Light Combat Plating
BioOutfit( "cortex.xml.template", {
    "typename":     typename["hull"],
    "size":         "small",
    "price":        lerpr( 120e3, 240e3 ),
    "mass":         60,
    "desc":         desc["hull"],
    "gfx_store":    "organic_hull_s.webp",
    "cargo":        lerpr(   4, 9 ),
    "absorb":       lerpr(   6, 12 ),
    "armour":       lerp(   90, 110 )
} ).run( [
    N_("Laevis Cortex I"),
    N_("Laevis Cortex II"),
] )

# Mediocre Cerebrum -> Orion_4801
BioOutfit( "cerebrum.xml.template", {
    "typename":     typename["brain"],
    "size":         "medium",
    "price":        lerpr(   (330e3+(185e3+75e3)/2)/2 , 330e3+(185e3+75e3)/2),
    "mass":         lerpr(90,90+(56+60)/2),
    "desc":         desc["brain"],
    "gfx_store":    "organic_core_m1.webp",
    "cpu":          lerpr(  80, 100 ),
    "shield" :      lerp(  450, 550 ),
    "shield_regen": lerp(   10,  13 ),
    "energy":       lerp(  750, 900 ),
    "energy_regen": lerp(   33,  56 ),
} ).run( [
    N_("Mediocre Cerebrum I"),
    N_("Mediocre Cerebrum II"),
] )

# Mediocris Gene Drive  =>  Tricon Cyclone
BioOutfit( "gene_drive.xml.template", {
    "typename":     typename["engine"],
    "size":         "medium",
    "price":        lerpr( 180e3, 360e3 ),
    "mass":         20,
    "desc":         desc["engine"],
    "gfx_store":    lerpt(("organic_engine_fast_m1.webp","organic_engine_fast_m2.webp")),
    "accel":        lerp(  110, 130 ),
    "turn":         lerp(   90, 115 ),
    "speed":        lerp(  190, 230 ),
    "fuel":         800,
    "energy_malus": lerp(   12,  12 ),
    "engine_limit": lerp(  630, 630 ),
} ).run( [
    N_("Mediocris Gene Drive I"),
    N_("Mediocris Gene Drive II"),
    N_("Mediocris Gene Drive III"),
] )

# Mediocris Cortex  =>  (1) Unicorp_d23  (2) S&K Medium Combat Plating
BioOutfit( "cortex.xml.template", {
    "typename":     typename["hull"],
    "size":         "medium",
    "price":        lerpr(  180e3, 360e3 ),
    "mass":         140,
    "desc":         desc["hull"],
    "gfx_store":    "organic_hull_m.webp",
    "cargo":        lerpr(  12,  19 ),
    "absorb":       lerpr(  20,  27 ),
    "armour":       lerp(  220, 320 )
} ).run( [
    N_("Mediocris Cortex I"),
    N_("Mediocris Cortex II")
] )

# Largum Cerebrum -> Orion_5501
BioOutfit( "cerebrum.xml.template", {
    "typename":     typename["brain"],
    "size":         "medium",
    "price":        lerpr(   (600e3+(185e3+75e3)/2)/2 , 600e3+(185e3+75e3)/2),
    "mass":         lerpr(270,270+(56+60)/2),
    "desc":         desc["brain"],
    "gfx_store":    "organic_core_m2.webp",
    "cpu":          lerpr( 200, 250 ),
    "shield" :      lerp(  580, 680 ), # was 700
    "shield_regen": lerp(   12,  15 ), # was 14
    "energy":       lerp( 1600, 1800 ),
    "energy_regen": lerp(   53,  87 ),
} ).run( [
    N_("Largum Cerebrum I"),
    N_("Largum Cerebrum II"),
] )

# Largus Gene Drive  =>  Tricon Cyclone II
BioOutfit( "gene_drive.xml.template", {
    "typename":     typename["engine"],
    "size":         "medium",
    "price":        lerpr(  337.5e3, 675e3 ),
    "mass":         25,
    "desc":         desc["engine"],
    "gfx_store":    lerpt(("organic_engine_strong_m1.webp","organic_engine_strong_m2.webp")),
    "accel":        lerp(   80, 100 ),
    "turn":         lerp(   75,  90 ),
    "speed":        lerp(  125, 175 ),
    "fuel":         1000,
    "energy_malus": lerp(   27,  27 ),
    "engine_limit": lerp( 1240, 1240 ),
} ).run( [
    N_("Largus Gene Drive I"),
    N_("Largus Gene Drive II"),
] )

# Largus Cortex  =>  (1) Unicorp_d38  (2) S&K Medium-Heavy Combat Plating
BioOutfit( "cortex.xml.template", {
    "typename":     typename["hull"],
    "size":         "medium",
    "price":        lerpr(  320e3, 640e3 ),
    "mass":         310,
    "desc":         desc["hull"],
    "gfx_store":    "organic_hull_l.webp",
    "cargo":        lerpr(  18,  34 ),
    "absorb":       lerpr(  35,  43 ),
    "armour":       lerp(  470, 660 )
} ).run( [
    N_("Largus Cortex I"),
    N_("Largus Cortex II"),
    N_("Largus Cortex III"),
] )

BioOutfit( "weapon.xml.template", {
    "typename": N_("Bioship Weapon Organ"),
    "size":     "large",
    "mass":     36,
    "price" :   lerpr(   0, 125e3 ),
    "desc":     N_("The Tentacle Organ has the distinction of being the only fully rotating organic weapon while boasting a fully developed power output that is hard to beat with conventional weaponry found throughout the galaxy. The large globs of hot plasma it launches can corrode through seemingly impregnable armours, seeping into and melting ships from the inside upon contact."),
    "gfx_store":"organic_plasma_t.webp",
    "specific": "turret bolt",
    "gfx":      "plasma.png",
    "gfx_end":  "plasma2-end.png",
    "sound":    "bioplasma_large",
    "spfx_shield":"ShiM",
    "spfx_armour":"PlaM",
    "lua":      "bioplasma.lua",
    "delay":    1.8,
    "speed" :   700,
    "range" :   lerp( 1800, 2000 ),
    "falloff":  lerp( 1500, 1800 ),
    "energy":   lerp(  155, 190 ),
    "trackmin": lerp( 3000, 4000 ),
    "trackmax": lerp(16000, 20000 ),
    "penetrate":lerpr(  70, 100 ),
    "damage":   lerp(   51,  65 ),
    "extra":    "<swivel>22</swivel>",
} ).run( [
    N_("Tentacle Organ I"),
    N_("Tentacle Organ II"),
    N_("Tentacle Organ III"),
    N_("Tentacle Organ IV")
] )

# Ponderosum Cerebrum -> Orion_8601
BioOutfit( "cerebrum.xml.template", {
    "typename":     typename["brain"],
    "size":         "large",
    "price":        lerpr(   3e6 , 3e6 ), # TODO
    "mass":         lerpr(540,540+(120+120)/2),
    "desc":         desc["brain"],
    "gfx_store":    "organic_core_l1.webp",
    "cpu":          lerpr( 350, 360 ),
    "shield" :      lerp(  850, 1050 ), # was already 1050
    "shield_regen": lerp(   15,  21 ),  # was 19
    "energy":       lerp( 2460, 3375 ),
    "energy_regen": lerp(  66, 135 ),
} ).run( [
    N_("Ponderosum Cerebrum I"),
    N_("Ponderosum Cerebrum II"),
    N_("Ponderosum Cerebrum III"),
] )

# Grandis Gene Drive  =>  Melendez Mammoth
BioOutfit( "gene_drive_melendez.xml.template", {
    "typename":     typename["engine"],
    "size":         "large",
    "price":        lerpr(  0.5625e6, 1.125e6 ),
    "mass":         75,
    "desc":         desc["engine"],
    "gfx_store":    lerpt(("organic_engine_fast_l1.webp","organic_engine_fast_l2.webp")),
    "accel":        lerp(   40,  47 ),
    "turn":         lerp(   42,  50 ),
    "speed":        lerp(   75,  90 ),
    "fuel":         2800,
    "energy_malus": lerp(   26,  26 ),
    "engine_limit": lerp( 3600, 3600 ),
} ).run( [
    N_("Grandis Gene Drive I"),
    N_("Grandis Gene Drive II"),
    N_("Grandis Gene Drive III"),
] )

# Ponderosus Gene Drive  =>  Tricon Typhoon
BioOutfit( "gene_drive.xml.template", {
    "typename":     typename["engine"],
    "size":         "large",
    "price":        lerpr(  1.35e6, 2.7e6 ),
    "mass":         60,
    "desc":         desc["engine"],
    "gfx_store":    lerpt(("organic_engine_fast_l1.webp","organic_engine_fast_l2.webp")),
    "accel":        lerp(   50,  65 ),
    "turn":         lerp(   65,  75 ),
    "speed":        lerp(   95,  115 ),
    "fuel":         2000,
    "energy_malus": lerp(   32,  32 ),
    "engine_limit": lerp( 2700, 2700 ),
} ).run( [
    N_("Ponderosus Gene Drive I"),
    N_("Ponderosus Gene Drive II"),
    N_("Ponderosus Gene Drive III"),
] )

# Ponderosus Cortex  =>  (1) Unicorp_d58  (2) S&K Heavy Combat Plating
BioOutfit( "cortex.xml.template", {
    "typename":     typename["hull"],
    "size":         "large",
    "price":        lerpr(  1.1e6, 2.2e6 ),
    "mass":         1150,
    "desc":         desc["hull"],
    "gfx_store":    "organic_hull_h.webp",
    "cargo":        lerpr(  55,  68 ),
    "absorb":       lerpr(  55,  63 ),
    "armour":       lerp( 1200, 1650 ),
} ).run( [
    N_("Ponderosus Cortex I"),
    N_("Ponderosus Cortex II"),
    N_("Ponderosus Cortex III"),
] )

# Immane Cerebrum -> Orion_9901
BioOutfit( "cerebrum.xml.template", {
    "typename":     typename["brain"],
    "size":         "large",
    "price":        lerpr(   4e6 , 4e6 ),
    "mass":         lerpr(1300,1300+(120+120)/2), # was 1400
    "desc":         desc["brain"],
    "gfx_store":    "organic_core_l2.webp",
    "cpu":          lerpr(1400, 1800 ),
    "shield" :      lerp(  1100, 1200 ),
    "shield_regen": lerp(   18,  22 ),
    "energy":       lerp( 3840, 5250 ),
    "energy_regen": lerp(  140, 170 ),
} ).run( [
    N_("Immane Cerebrum I"),
    N_("Immane Cerebrum II"),
    N_("Immane Cerebrum III"),
] )

# Immanis Gene Drive  =>  Eagle 6500
BioOutfit( "gene_drive.xml.template", {
    "typename":     typename["engine"],
    "size":         "large",
    "price":        lerpr(   0.2e6, 0.4e6 ),
    "mass":         65,
    "desc":         desc["engine"],
    "gfx_store":    lerpt(("organic_engine_strong_l1.webp","organic_engine_strong_l2.webp")),
    "accel":        lerp(   30,  37 ),
    "turn":         lerp(   35,  45 ),
    "speed":        lerp(   60,  70 ),
    "fuel":         2800,
    "energy_malus": lerp(   40,  40 ),
    "engine_limit": lerp( 6500, 6500 ),
} ).run( [
    N_("Immanis Gene Drive I"),
    N_("Immanis Gene Drive II"),
    N_("Immanis Gene Drive III"),
] )

# Magnus Gene Drive  =>  Tricon Typhoon2
BioOutfit( "gene_drive.xml.template", {
    "typename":     typename["engine"],
    "size":         "large",
    "price":        lerpr(   1.8e6, 3.6e6 ),
    "mass":         80,
    "desc":         desc["engine"],
    "gfx_store":    lerpt(("organic_engine_strong_l1.webp","organic_engine_strong_l2.webp")),
    "accel":        lerp(   40,  50 ),
    "turn":         lerp(   46,  60 ),
    "speed":        lerp(   70,  80 ),
    "fuel":         2400,
    "energy_malus": lerp(   56,  56 ),
    "engine_limit": lerp( 5800 , 5800),
} ).run( [
    N_("Magnus Gene Drive I"),
    N_("Magnus Gene Drive II"),
    N_("Magnus Gene Drive III"),
] )

# Immanis Cortex  =>  (1) Unicorp_d72  (2) S&K Superheavy Combat Plating
BioOutfit( "cortex.xml.template", {
    "typename":     typename["hull"],
    "size":         "large",
    "price":        lerpr(   1.45e6, 2.9e6 ),
    "mass":         1250,
    "desc":         desc["hull"],
    "gfx_store":    "organic_hull_x.webp",
    "cargo":        lerpr(  80, 120 ),
    "absorb":       lerpr(  69, 77 ),
    "armour":       lerpr( 1700, 2400 )
} ).run( [
    N_("Immanis Cortex I"),
    N_("Immanis Cortex II"),
    N_("Immanis Cortex III"),
] )


