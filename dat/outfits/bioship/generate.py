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

def lerpr( a, b ):
    return lambda x: int(round(a + x * (b-a)))

def lerp( a, b ):
    return lambda x: a + x * (b-a)

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

BioOutfit( "weapon.xml.template", {
    "typename": N_("Bioship Weapon Organ"),
    "size":     "small",
    "mass":     6,
    "price" :   lerpr(   0, 20e3 ),
    "desc":     N_("The Stinger Organ is able to convert energy into hot plasma that is able to eat easily eat through shield and armour of opposing ships over time. While not an especially powerful offensive organ, it is prized for its reliability."),
    "gfx_store":lerpt(("organic_plasma_s1.webp", "organic_plasma_s2.webp","organic_plasma_s3.webp")),
    "specific": "bolt",
    "gfx":      "plasma.png",
    "gfx_end":  "plasma2-end.png",
    "sound":    "bioplasma",
    "spfx_shield":"ShiS",
    "spfx_armour":"PlaS",
    "lua":      "bioplasma.lua",
    "delay":    1.2,
    "speed" :   lerp(  600, 600 ),
    "range" :   lerp(  650, 800 ),
    "falloff":  lerp(  450, 600 ),
    "energy":   lerpr(   9,  15 ),
    "trackmin": 0,
    "trackmax": 2000,
    "penetrate":lerpr(   6,  12 ),
    "damage":   lerp(   18,  27 ),
    "extra":    "<swivel>22</swivel>",
} ).run( [
    N_("Stinger Organ I"),
    N_("Stinger Organ II"),
    N_("Stinger Organ III"), # TODO make stronger
] )

BioOutfit( "cerebrum.xml.template", {
    "typename":     typename["brain"],
    "size":         "small",
    "price":        lerpr(   0, 120e3 ),
    "mass":         14,
    "desc":         desc["brain"],
    "gfx_store":    "organic_core_s1.webp",
    "cpu":          lerpr(   5,   8 ),
    "shield" :      lerp(  200, 250 ),
    "shield_regen": lerp(    6,   9 ),
    "energy":       lerp(  200, 250 ),
    "energy_regen": lerp(   14,  19 ),
} ).run( [
    N_("Perleve Cerebrum I"),
    N_("Perleve Cerebrum II"),
] )

BioOutfit( "gene_drive.xml.template", {
    "typename":     typename["engine"],
    "size":         "small",
    "price":        lerpr(   0, 140e3 ),
    "mass":         8,
    "desc":         desc["engine"],
    "gfx_store":    lerpt(("organic_engine_fast_s1.webp","organic_engine_fast_s2.webp")),
    "accel":        lerp(  165, 196 ),
    "turn":         lerp(  130, 160 ),
    "speed":        lerp(  295, 345 ),
    "fuel":         400,
    "energy_malus": lerp(    5,   5 ),
    "engine_limit": lerp(  150, 150 ),
} ).run( [
    N_("Perlevis Gene Drive I"),
    N_("Perlevis Gene Drive II"),
] )

BioOutfit( "cortex.xml.template", {
    "typename":     typename["hull"],
    "size":         "small",
    "price":        lerpr(   0, 130e3 ),
    "mass":         30,
    "desc":         desc["hull"],
    "gfx_store":    "organic_hull_t.webp",
    "cargo":        lerpr(   4, 4 ),
    "absorb":       lerpr(   1, 3 ),
    "armour":       lerp(   45, 65 )
} ).run( [
    N_("Perlevis Cortex I"),
    N_("Perlevis Cortex II"),
] )

BioOutfit( "cerebrum.xml.template", {
    "typename":     typename["brain"],
    "size":         "small",
    "price":        lerpr(   0, 210e3 ),
    "mass":         50,
    "desc":         desc["brain"],
    "gfx_store":    "organic_core_s2.webp",
    "cpu":          lerpr(  24,  32 ),
    "shield" :      lerp(  250, 310 ),
    "shield_regen": lerp(    6,  10 ),
    "energy":       lerp(  330, 400 ),
    "energy_regen": lerp(   28,  34 ),
} ).run( [
    N_("Laevum Cerebrum I"),
    N_("Laevum Cerebrum II"),
] )

BioOutfit( "gene_drive.xml.template", {
    "typename":     typename["engine"],
    "size":         "small",
    "price":        lerpr(   0, 90e3 ),
    "mass":         15,
    "desc":         desc["engine"],
    "gfx_store":    lerpt(("organic_engine_strong_s1.webp","organic_engine_strong_s2.webp")),
    "accel":        lerp(  100, 115 ),
    "turn":         lerp(   80,  95 ),
    "speed":        lerp(  190, 225 ),
    "fuel":         500,
    "energy_malus": lerp(    7,   7 ),
    "engine_limit": lerp(  400, 400 ),
} ).run( [
    N_("Laevis Gene Drive I"),
    N_("Laevis Gene Drive II"),
] )

BioOutfit( "weapon.xml.template", {
    "typename": N_("Bioship Weapon Organ"),
    "size":     "medium",
    "mass":     30,
    "price" :   lerpr(   0, 20e3 ),
    "desc":     N_("The Talon Organ is an enlarged and more powerful version of the Stinger Organ. Like its smaller counterpart, is able to convert energy into hot plasma that is able to eat easily eat through shield and armour of opposing ships. The hot plasma is able to cling to ship's shields and hulls dealing continuous damage after impact."),
    "gfx_store":"organic_plasma_l.webp",
    "specific": "bolt",
    "gfx":      "plasma2.png",
    "gfx_end":  "plasma2-end.png",
    "sound":    "bioplasma",
    "spfx_shield":"ShiS",
    "spfx_armour":"PlaS2",
    "lua":      "bioplasma2.lua",
    "delay":    1.4,
    "speed" :   lerp(  600, 600 ),
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

BioOutfit( "cortex.xml.template", {
    "typename":     typename["hull"],
    "size":         "small",
    "price":        lerpr(   0, 240e3 ),
    "mass":         60,
    "desc":         desc["hull"],
    "gfx_store":    "organic_hull_s.webp",
    "cargo":        lerpr(   9, 9 ),
    "absorb":       lerpr(   3, 6 ),
    "armour":       lerp(   85, 110 )
} ).run( [
    N_("Laevis Cortex I"),
    N_("Laevis Cortex II"),
] )

BioOutfit( "cerebrum.xml.template", {
    "typename":     typename["brain"],
    "size":         "medium",
    "price":        lerpr(   0, 330e3 ),
    "mass":         90,
    "desc":         desc["brain"],
    "gfx_store":    "organic_core_m1.webp",
    "cpu":          lerpr(  80, 100 ),
    "shield" :      lerp(  460, 550 ),
    "shield_regen": lerp(    9,  13 ),
    "energy":       lerp(  750, 900 ),
    "energy_regen": lerp(   46,  56 ),
} ).run( [
    N_("Mediocre Cerebrum I"),
    N_("Mediocre Cerebrum II"),
] )

BioOutfit( "gene_drive.xml.template", {
    "typename":     typename["engine"],
    "size":         "medium",
    "price":        lerpr(   0, 360e3 ),
    "mass":         20,
    "desc":         desc["engine"],
    "gfx_store":    lerpt(("organic_engine_fast_m1.webp","organic_engine_fast_m2.webp")),
    "accel":        lerp(  110, 130 ),
    "turn":         lerp(   90, 115 ),
    "speed":        lerp(  190, 230 ),
    "fuel":         800,
    "energy_malus": lerp(   10,  10 ),
    "engine_limit": lerp(  550, 550 ),
} ).run( [
    N_("Mediocris Gene Drive I"),
    N_("Mediocris Gene Drive II"),
    N_("Mediocris Gene Drive III"),
] )

BioOutfit( "cortex.xml.template", {
    "typename":     typename["hull"],
    "size":         "medium",
    "price":        lerpr(   0, 360e3 ),
    "mass":         110,
    "desc":         desc["hull"],
    "gfx_store":    "organic_hull_m.webp",
    "cargo":        lerpr(  18,  18 ),
    "absorb":       lerpr(  11,  15 ),
    "armour":       lerp(  230, 300 )
} ).run( [
    N_("Mediocris Cortex I"),
    N_("Mediocris Cortex II")
] )

BioOutfit( "cerebrum.xml.template", {
    "typename":     typename["brain"],
    "size":         "medium",
    "price":        lerpr(   0, 600e3 ),
    "mass":         200,
    "desc":         desc["brain"],
    "gfx_store":    "organic_core_m2.webp",
    "cpu":          lerpr( 200, 250 ),
    "shield" :      lerp(  550, 700 ),
    "shield_regen": lerp(    9,  14 ),
    "energy":       lerp( 1450, 1800 ),
    "energy_regen": lerp(   72,  87 ),
} ).run( [
    N_("Largum Cerebrum I"),
    N_("Largum Cerebrum II"),
] )

BioOutfit( "gene_drive.xml.template", {
    "typename":     typename["engine"],
    "size":         "medium",
    "price":        lerpr(   0, 360e3 ),
    "mass":         25,
    "desc":         desc["engine"],
    "gfx_store":    lerpt(("organic_engine_strong_m1.webp","organic_engine_strong_m2.webp")),
    "accel":        lerp(   80, 100 ),
    "turn":         lerp(   75,  90 ),
    "speed":        lerp(  125, 175 ),
    "fuel":         800,
    "energy_malus": lerp(   15,  15 ),
    "engine_limit": lerp( 1200, 1200 ),
} ).run( [
    N_("Largus Gene Drive I"),
    N_("Largus Gene Drive II"),
] )

BioOutfit( "cortex.xml.template", {
    "typename":     typename["hull"],
    "size":         "medium",
    "price":        lerpr(   0, 640e3 ),
    "mass":         310,
    "desc":         desc["hull"],
    "gfx_store":    "organic_hull_l.webp",
    "cargo":        lerpr(  36,  36 ),
    "absorb":       lerpr(  20,  30 ),
    "armour":       lerp(  570, 660 )
} ).run( [
    N_("Largus Cortex I"),
    N_("Largus Cortex II"),
    N_("Largus Cortex III"),
] )

BioOutfit( "weapon.xml.template", {
    "typename": N_("Bioship Weapon Organ"),
    "size":     "large",
    "mass":     75,
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
    "speed" :   lerp(  600, 600 ),
    "range" :   lerp( 1800, 2000 ),
    "falloff":  lerp( 1500, 1800 ),
    "energy":   lerp(  155, 190 ),
    "trackmin": lerp( 3000, 4000 ),
    "trackmax": lerp(16000, 20000 ),
    "penetrate":lerpr(  70, 100 ),
    "damage":   lerp(   51,  65 ),
    "extra":    "",
} ).run( [
    N_("Tentacle Organ I"),
    N_("Tentacle Organ II"),
    N_("Tentacle Organ III"),
    N_("Tentacle Organ IV")
] )

BioOutfit( "cerebrum.xml.template", {
    "typename":     typename["brain"],
    "size":         "large",
    "price":        lerpr(   0, 3e6 ),
    "mass":         660,
    "desc":         desc["brain"],
    "gfx_store":    "organic_core_l1.webp",
    "cpu":          lerpr( 360, 350 ),
    "shield" :      lerp(  800, 1050 ),
    "shield_regen": lerp(   11,  19 ),
    "energy":       lerp( 2900, 3375 ),
    "energy_regen": lerp(  105, 135 ),
} ).run( [
    N_("Ponderosum Cerebrum I"),
    N_("Ponderosum Cerebrum II"),
    N_("Ponderosum Cerebrum III"),
] )

BioOutfit( "gene_drive.xml.template", {
    "typename":     typename["engine"],
    "size":         "large",
    "price":        lerpr(   0, 11e6 ),
    "mass":         75,
    "desc":         desc["engine"],
    "gfx_store":    lerpt(("organic_engine_fast_l1.webp","organic_engine_fast_l2.webp")),
    "accel":        lerp(   40,  47 ),
    "turn":         lerp(   42,  50 ),
    "speed":        lerp(   75,  90 ),
    "fuel":         2000,
    "energy_malus": lerp(   25,  25 ),
    "engine_limit": lerp( 3600, 3600 ),
} ).run( [
    N_("Ponderosus Gene Drive I"),
    N_("Ponderosus Gene Drive II"),
    N_("Ponderosus Gene Drive III"),
] )

BioOutfit( "cortex.xml.template", {
    "typename":     typename["hull"],
    "size":         "medium",
    "price":        lerpr(   0, 22e6 ),
    "mass":         1150,
    "desc":         desc["hull"],
    "gfx_store":    "organic_hull_h.webp",
    "cargo":        lerpr(  70,  70 ),
    "absorb":       lerpr(  44,  56 ),
    "armour":       lerp( 1300, 1650 ),
} ).run( [
    N_("Ponderosus Cortex I"),
    N_("Ponderosus Cortex II"),
    N_("Ponderosus Cortex III"),
] )

BioOutfit( "cerebrum.xml.template", {
    "typename":     typename["brain"],
    "size":         "large",
    "price":        lerpr(   0, 4e6 ),
    "mass":         1400,
    "desc":         desc["brain"],
    "gfx_store":    "organic_core_l2.webp",
    "cpu":          lerpr(1400, 1800 ),
    "shield" :      lerp(  950, 1200 ),
    "shield_regen": lerp(   17,  22 ),
    "energy":       lerp( 4200, 5250 ),
    "energy_regen": lerp(  145, 170 ),
} ).run( [
    N_("Immane Cerebrum I"),
    N_("Immane Cerebrum II"),
    N_("Immane Cerebrum III"),
] )

BioOutfit( "gene_drive.xml.template", {
    "typename":     typename["engine"],
    "size":         "large",
    "price":        lerpr(   0, 3.6e6 ),
    "mass":         100,
    "desc":         desc["engine"],
    "gfx_store":    lerpt(("organic_engine_strong_l1.webp","organic_engine_strong_l2.webp")),
    "accel":        lerp(   28,  35 ),
    "turn":         lerp(   35,  45 ),
    "speed":        lerp(   60,  70 ),
    "fuel":         1600,
    "energy_malus": lerp(   45,  45 ),
    "engine_limit": lerp( 6800, 6800 ),
} ).run( [
    N_("Immanis Gene Drive I"),
    N_("Immanis Gene Drive II"),
    N_("Immanis Gene Drive III"),
] )

BioOutfit( "cortex.xml.template", {
    "typename":     typename["hull"],
    "size":         "large",
    "price":        lerpr(   0, 2.9e6 ),
    "mass":         1950,
    "desc":         desc["hull"],
    "gfx_store":    "organic_hull_x.webp",
    "cargo":        lerpr(  90, 90 ),
    "absorb":       lerpr(  67, 80 ),
    "armour":       lerp( 1900, 2400 )
} ).run( [
    N_("Immanis Cortex I"),
    N_("Immanis Cortex II"),
    N_("Immanis Cortex III"),
] )
