Below is an updated, extremely detailed game specification for a Myth-style real-time tactical strategy game set in the Rick and Morty universe without any single hero units. In other words, you command squads of standard soldiers analogous to Myth’s Warriors, Bowmen, Dwarves, Berserks, etc., rather than unique characters like Rick or Morty in hero roles. These squads appear in appropriate numbers (just like Myth’s multiple warriors and archers) and maintain the tactical, physics-driven gameplay of Myth II. Everything else—physics, camera, single-player structure—remains faithful to Myth II, but thematically wrapped in Rick and Morty style.

1. Core Gameplay
1.1 Overview
Genre & Inspiration: A real-time tactical strategy game directly inspired by Myth: The Fallen Lords and Myth II: Soulblighter. You control squads of units in combat; no base building, no resource farming.
Setting & Tone: Entirely set in the Rick and Morty multiverse. However, instead of commanding unique hero characters (Rick, Morty, Birdperson, etc.), you command squads of “multiversal troopers” that carry the thematic flair—e.g. Morty Clones as infantry, Portal Archers, Meeseeks Berserkers, and so on.
Squad-Based Tactics: Each mission starts with a fixed roster of unit squads. Losses are permanent. Missions revolve around survival, smart positioning, and synergy among different unit types.
No Heroes: Where Myth might give you one “heroic dwarf” or “named archer,” this specification avoids single named heroes. Instead, you’ll have multiple “Tech Grenadiers” or “Meeseeks Berserkers,” etc. Even if the story references Rick or Morty, they are not individual playable units with unique stats; they’re off-screen or cameo.
1.2 Key Gameplay Elements
Formation & Terrain
As in Myth, formations are crucial. Squads can be arranged in lines, wedges, or columns. Position your squads on high ground for range and visibility advantages; use choke points and flanks.
Terrain height affects projectile arcs, line of sight, and movement speed (uphill/downhill).
Friendly Fire
All ranged and explosive attacks are fully physics-based; there is no “safe” targeting. You must carefully position squads so you don’t blow up your own ranks.
Lethal Combat
Each squad has relatively low health, reflecting Myth’s lethal design. A few hits or a single explosion can wipe out a squad if you’re careless.
Cinematic Battles
Corpses, gore, and debris remain on the battlefield, dynamic ragdolls fling across the map, and craters form from explosions. This gritty realism is retained, albeit with a comedic Rick and Morty flavor (e.g., a Morty Clone’s severed arm might still be yelling comedic lines).
2. Physics System
Mirroring Myth II’s robust projectile and explosion physics:

Projectile Arcs
Arrows, crossbow bolts, and grenades are actual physics objects. They have trajectories influenced by gravity, movement of targets, and collisions with terrain/obstacles.
Explosions & Knockback
Grenades or explosive devices produce blasts that fling units. Body parts can be severed and sent flying. Craters form in the terrain.
Persistent Debris
Corpses and severed parts remain. They can be moved by subsequent blasts, causing chain reactions. The battlefield ends up littered with comedic carnage: “Morty Clone limbs”, Gromflomite shells, etc.
Chain Reactions
Explosive chain reactions can occur if you detonate a stockpile of bombs or if one squad’s grenadier inadvertently hits another. This emergent chaos is part of the tactical puzzle.
For simplicity, we replicate exactly the Myth II physics scale (grenade radius, projectile speeds, etc.), but re-skinned in a sci-fi cartoon style.

3. 3D Camera System
Stay true to Myth II:

Eight Fixed Angles
The camera can rotate around the battlefield in 45° increments.
Zoom & Pitch
A limited tilt range (e.g. 45–60° from overhead). Scroll or pinch to zoom in/out.
Field of View & Panning
Adjustable FOV slider to see more or less at once.
Pan by edge scrolling or keyboard input.
Sprite-Based Units in 3D Terrain
Each unit is an 8-directional sprite (or 16 if extra detail is desired), seamlessly integrated on a fully 3D environment.
4. Art Style & Graphics
4.1 Unit Sprites
2D Sprites: All units are drawn from 8 angles, matching camera constraints. They animate for movement, attacks, death, etc.
Squad Variation: Each squad is composed of multiple identical sprites (or slight variations: different hair color, armor tints, etc.) to give a sense of an actual group rather than clones.
Rick and Morty Flavor: Despite being “standard” soldiers, their look/voice lines evoke the show—like Morty Clones each wearing color-coded jumpsuits, or Meeseeks Berserkers in tribal gear.
4.2 Terrain & Visual Effects
3D Terrain: Rolling hills, alien landscapes, futuristic cityscapes. Painted or stylized to keep a comedic, cartoonish vibe but with enough detail for tactical clarity.
Explosive Effects: Particle systems for fire, plasma bursts, comedic greenish blood, etc.
Performance: Built for MacBook Pro M4 Ultra, so you can have large squads and lots of gore at high framerates.
5. Singleplayer Campaign: Structure & Missions
While we’re removing named hero units, we still have a narrative framework:

Campaign Scope
A short set of missions (3–5) featuring large-scale battles. Each mission gives you a squad lineup of “light side” units and tasks you with objectives.
Narrative Flavor
Rick or Morty might appear in mission briefings (voiceover or cameo), but on the battlefield, you only control squads of rank-and-file troopers (like “Tech Grenadiers,” “Portal Archers,” etc.).
Missions revolve around comedic Rick and Morty scenarios: defend a dimension from Cronenberg hordes, repel a Gromflomite assault on a ruined Citadel, etc.
5.1 Example Mission Flow
Mission 1: “Citadel Crisis”
You command a handful of squads from the Citadel Army (see “Light Side Units” below) to repel an uprising of rogue Mortys. Terrain is a futuristic Citadel courtyard. The mission teaches movement, formations, and ranged vs. melee synergy.
Mission 2: “Purge Planet Patrol”
On a planet where an annual Purge is happening, your squads must escort a convoy. Enemies are rabid Purge locals. Emphasizes covering flanks, maintaining formation under ambush.
Mission 3: “Cronenberg Infestation”
Survive waves of Cronenberg monsters in a ruined dimension. The monsters come from multiple angles. The squads that remain get carried over to the next mission.
Final Mission: “Showdown at Blood Ridge”
An homage to Myth and the Rick and Morty lore, you have a large force. Gromflomite shock troopers assault your entrenched line. The mission ends with an explosive final set-piece. No single heroes—just your squads valiantly holding the ridge.
6. Light Side Units (No Heroes)
Below are five staple unit types analogous to Myth’s Warriors, Archers, Dwarves, Berserks, and Journeymen—but all standard squads. You can start a mission controlling, for example, 10 squads of Dimensioneers, 4 squads of Portal Archers, etc. The exact quantity depends on mission design.

Naming Convention: Each “squad” might represent ~3 to 5 identical sprite troopers that act as one “unit group” from the player’s perspective. You see multiple troopers, but they share a single “health pool” (for simplicity), or optionally each trooper can be individually killable (like Myth did with single units).

6.1 Dimensioneers (Melee Infantry)
Myth Analog: Warrior
Description:
A standard, disciplined foot soldier from the “Dimensioneer Corps.” Each wears a patch with a stylized portal on the armor. They carry some form of futuristic polearm or shock-sword.
Lore-wise, these troopers are recruited across infinite realities to serve in the Citadel’s defensive forces (or some faction that the player commands).
Combat Role:
Frontline: They form the backbone of your army, holding the line against enemy charges.
Stats: Moderate health/armor, average speed, steady damage.
Attack: Melee slash or thrust with a modest attack rate.
Special Trait: Slightly more resilient to knockback (the synergy with Myth’s Warriors being well-rounded).
Behavior:
They maintain formation well, can brace for incoming charges, and won’t break rank easily.
If you give them a move order behind an obstacle, they find a path around it. They do not automatically chase enemies far.
6.2 Portal Archers
Myth Analog: Bowman
Description:
Ranged squads armed with “portal-bow rifles” or crossbows that shoot small energy bolts or arrow-like projectiles. They wear lighter armor and have comedic commentary about “aiming across dimensions.”
Combat Role:
Long-range support: They pepper enemies from behind your frontline.
Stats: Low health, minimal armor, modest movement speed.
Attack: Arcing energy arrows with ballistic drop. High range but slower rate of fire.
Special Trait: Possibly able to fire “phasing arrows” that can bypass a thin obstacle once every so often (like a volley shot in Myth).
Behavior:
If not micromanaged, they’ll automatically target the closest enemy but hold fire if friendly units block their line of shot (to reduce friendly fire).
They’re vulnerable to enemy rushes, so keep them protected.
6.3 Tech Grenadiers
Myth Analog: Dwarf
Description:
Explosive experts in advanced exosuits. They lob “tech grenades” that produce high-damage AoE blasts. Their comedic flair: each sports a little “Rick-styled” lab coat or goggles, referencing the origin of their gear, but they are not Rick himself.
Combat Role:
AoE damage: Perfect for dealing with clustered enemies. They can decimate large groups but risk hitting allies if used recklessly.
Stats: Low health, slow movement (because of gear), limited ammo for grenades (e.g., 6–8 per mission).
Attack: Grenade toss in an arc. Large explosion radius, high friendly-fire potential.
Special Trait: Each squad might carry a single “mega-bomb” with a bigger radius but slower throw or a timed delay.
Behavior:
They try to avoid suicidal throws if allies are too close, but in the heat of battle, accidents happen.
Best stationed behind your melee lines or on high ground to lob bombs over.
6.4 Meeseeks Berserkers
Myth Analog: Berserk
Description:
Squads of savage, hyper-aggressive Mr. Meeseeks in battered armor, each repeated as “I’m Mr. Meeseeks, let me fight!” They exist in indefinite agony until they fulfill “the job”—which is apparently to tear enemies apart.
Combat Role:
Shock troops: Very high melee damage and speed, minimal armor.
Stats: Above-average health but no real protection; they rely on speed and aggression.
Attack: Frenzied melee strikes with large swords, clubs, or even improvised scythes.
Special Trait: Extra damage vs. large targets. Possibly a leap attack that closes distance quickly.
Behavior:
They never retreat—always charge. This is extremely valuable for flanking or quick strikes but can lead to heavy losses if poorly managed.
They utter comedic lines referencing existence pain.
6.5 Poopy Medics
Myth Analog: Journeyman
Description:
Humanoid squads wearing bandoliers of sci-fi medical syringes and spouting polite, enthusiastic lines reminiscent of “Mr. Poopybutthole.” They are not single named characters but a group of them.
Combat Role:
Support & Healing: They can restore health to friendly squads in limited amounts (like how Journeymen carried healing mandrake roots).
Stats: Average speed, light armor, poor offense.
Attack: Basic melee or a short-range stun dart. Very weak, purely defensive.
Special Trait: They carry a finite number of “healing injectors,” so you must use them judiciously. Possibly they can resurrect a fallen trooper if done quickly after death (like Myth II’s Journeyman seeds).
Behavior:
Will stay behind the lines, attempt to auto-heal nearby squads that are injured. They avoid direct contact with enemies.
Note: You can choose to exclude or include these “Poopy Medics” if you want a purely lethal game with no healing, but many Myth players appreciate having a small healing resource.

7. Enemy Units (Dark Side)
You’ll face large waves of units paralleling the Myth bestiary—thralls, fetch, etc.—but re-themed:

Gromflomite Soldiers (Analogous to Thrall or standard melee)
Basic foot soldiers. Some squads carry rifles (ranged), others have spears (melee). They come in large numbers.
Cronenberg Horrors (Analogous to Myrkridia)
Fast, feral monsters. Melee only, dealing huge damage, suicidally rushing your lines. On death, they might explode in toxic gore.
Federation Grenadiers (Analogous to Myrmidon or dwarf-like enemies)
These squads lob plasma grenades at your formations. Extremely dangerous if left unchecked.
Hover Drones (Analogous to Soulless)
Ranged floating units that fire from a distance. Harder to hit due to flight.
Mutated Berserkers or Evil Morty Troopers (Analogous to Trow or boss-tier enemies)
Elite squads with massive health and destructive attacks, typically final-wave threats.
Enemies also appear in squads of multiple troopers or creatures. They often coordinate in waves or formations with a large variety, forcing you to use your own combined-arms approach.

8. AI System
8.1 Friendly Unit AI (Squad-Based)
Formation Logic: Dimensioneers and Archers maintain formations if you group them. Meeseeks Berserkers do not hold formation well (they charge).
Auto-Fire & Self-Preservation: Ranged squads do not shoot if allies block line of sight. Grenadiers hesitate if it will cause friendly fire, but not always.
Healing Priority: Poopy Medics will attempt to heal squads with the lowest health first, if resources remain.
8.2 Enemy AI
Squad Behavior: Groups of Gromflomites or Cronenbergs spawn and attack from logical routes, sometimes flanking or combining ranged + melee.
Morale: Basic enemies might retreat if half their squad is wiped out quickly. Cronenbergs never retreat.
Cover & Avoid Hazards: If there’s obviously deadly terrain (fire, acid), enemy squads route around it (like Myth II).
8.3 Physics-Aware Tactics
Both friendly and enemy grenadiers consider arcs, line of sight, and friendly forces before throwing. Minor variations in aim produce realistic misses and unpredictability.

9. Implementation & Technical Details
Engine & Rendering

2D sprite sheets for each unit type, pre-rendered from 8 angles. Each squad is several identical sprites that move in tight formation.
3D terrain with heightmaps, obstacles, and pathfinding.
Metal API on MacBook Pro M4 Ultra for optimized performance.
Physics Library

A simplified custom system or a library (e.g., Bullet) to handle projectile arcs, collisions, ragdoll, and explosive impulses.
Ragdoll for a squad can be abstracted (either each trooper is tracked separately or the whole group has partial ragdoll events).
AI Scripting

Behavior trees or state machines controlling how squads move, form up, seek cover, or charge.
Enemy wave triggers and pathing set in mission scripts.
No Single Heroes

All unique references to “Rick” or “Morty” are either off-screen or cameo. The squads themselves are generalized “Morty Clone Archers,” “Rickish Grenadiers,” etc. This fosters that Myth feeling of controlling many identical units.
User Interface

A top-down “squad panel” that shows each squad icon, health bar, and ammo count if applicable (e.g. Tech Grenadiers have a grenade counter).
Formation hotkeys for line, box, wedge.
Mini-map with your squads in one color and enemies (once spotted) in another.
Difficulty & Tuning

Missions are balanced around typical Myth II difficulty: combat is swift and punishing if you mismanage squads.
Adjust factors (enemy count, AI aggression, projectile damage) to create multiple difficulty modes.
10. Example Squad Composition
A typical mid-game mission might give you:

4 squads of Dimensioneers (each squad has ~3–5 melee troopers)
2 squads of Portal Archers (3–5 archers each)
1 squad of Tech Grenadiers (3 engineers with a total of 8 grenades)
2 squads of Meeseeks Berserkers (5 meeseeks each)
1 squad of Poopy Medics (3–5 medics, each with a few heal charges)
You’ll face, say, waves of Gromflomite squads supported by Hover Drones. Surviving squads gain slight experience (better accuracy or morale) going into the next mission, encouraging you to keep them alive.

11. Campaign Progression (No Named Heroes)
Even though there are no single heroes, you can preserve Myth-style continuity:

Carryover: If you keep a squad mostly alive from one mission to the next, that squad has improved stats or a special trait. E.g., a Dimensioneer squad might eventually become “Veteran Dimensioneers” with +10% damage.
Permanent Loss: If a squad is wiped out, you don’t get it back next mission. This can drastically change your tactics in later missions if you lost your only Tech Grenadiers.
Story Delivery: Briefings and debriefings might show comedic dialogues or cutscenes from Rick, Morty, or others talking about your performance, but they are not units on the field. You direct the “nameless masses” who do the actual fighting.
12. Summary
Objective: Create a Myth II-style tactical RTS, using squads reminiscent of Myth’s classic unit types—no single hero or unique named characters in direct control. The game retains:

Physics: Realistic projectiles, big explosions, destructive chain reactions.
Camera: 8-direction lock, zoom, pitch, full battlefield awareness.
Art Style: Sprite-based units on 3D terrain, comedic Rick and Morty re-skin with gore.
AI: Formation logic, self-preservation, flanking, retreat, etc.
Singleplayer Missions: Intense battles with unique objectives. Potential carryover of surviving squads.
Rick & Morty Flavor: Off-the-wall humor, references, but no “heroic Rick” overshadowing the gameplay. Instead, you command squads of “Portal Archers,” “Dimensioneers,” “Meeseeks Berserkers,” etc.
With this approach, you capture the large-scale squad tactics and chaotic physics that Myth fans love, while keeping it fresh, comedic, and accessible for a proof-of-concept on the powerful MacBook Pro M4 Ultra. No individual hero units are needed—players will experience epic Rick and Morty battles purely through a vast array of rank-and-file troopers, each with that signature comedic twist.