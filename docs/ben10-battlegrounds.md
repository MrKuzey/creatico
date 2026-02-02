# Ben 10 Battlegrounds (Roblox) — Game Design Doc

## Vision
A fast-paced battlegrounds-style Roblox experience inspired by the Ben 10 universe. Players transform into aliens with distinct playstyles, clash in short rounds, and earn DNA Points to unlock cosmetics and upgrades. The core loop emphasizes movement skill, timing, and transforming at the right moment.

## Core Pillars
1. **Transform & Dominate:** Each alien has a unique movement and combat kit.
2. **Fast Rounds:** 6–10 minutes per match with quick respawns.
3. **Skill Expression:** Combos, aerial plays, and terrain mastery.
4. **Progression:** Earn DNA Points, unlock alien variants, and cosmetic effects.

## Player Count & Match Flow
- **Mode:** 8–16 players in a free-for-all or 4v4 team variant.
- **Round Length:** 6–10 minutes.
- **Win Condition:** Highest eliminations or team score at timer end.
- **Respawn:** 3–5 seconds.

## Transformations (Minimum 5)
Each alien has **Primary**, **Secondary**, **Mobility**, and **Ultimate** abilities.

### 1) Heatblast (Ranged DPS)
- **Primary:** Fireball — fast, medium damage projectile.
- **Secondary:** Flame Wall — short-lived barrier that blocks shots.
- **Mobility:** Jet Burst — short dash with burning trail.
- **Ultimate:** Meteor Burst — area explosion with lingering fire.

### 2) Four Arms (Bruiser)
- **Primary:** Heavy Punch — strong melee combo.
- **Secondary:** Ground Slam — radial knockback.
- **Mobility:** Leap Smash — leap forward and impact.
- **Ultimate:** Rage Mode — increased attack speed & resistance.

### 3) XLR8 (Speed Skirmisher)
- **Primary:** Rapid Strikes — quick melee chain.
- **Secondary:** Vortex Kick — spin kick that pulls enemies in.
- **Mobility:** Speed Trail — high-speed sprint with wall-run.
- **Ultimate:** Time Dilation — slows enemies briefly in an area.

### 4) Diamondhead (Tank/Control)
- **Primary:** Crystal Shards — short-range burst.
- **Secondary:** Crystal Shield — frontal damage reduction.
- **Mobility:** Crystal Slide — low friction glide.
- **Ultimate:** Crystal Cage — traps enemies in a prism.

### 5) Cannonbolt (Disruptor)
- **Primary:** Roll Impact — damaging roll on contact.
- **Secondary:** Bounce Shock — bounce and knock enemies back.
- **Mobility:** Shell Rush — accelerates to max speed.
- **Ultimate:** Cannon Crash — high-speed slam with big knockback.

> **Stretch Aliens:** Wildmutt (tracker), Upgrade (tech control), Ghostfreak (stealth), Stinkfly (air control), Ripjaws (water).

## Controls (PC + Mobile)
- **Primary Attack:** Mouse / Tap
- **Secondary:** Q / Button 2
- **Mobility:** E / Button 3
- **Ultimate:** R / Button 4
- **Transform Wheel:** T / Button 5
- **Sprint:** Shift / Toggle

## Game Loop
1. **Queue & Loadout:** Choose 2–3 aliens (rotation if needed).
2. **Match Start:** Drop into arena, Omnitrix charge at 100%.
3. **Combat:** Transform, fight, recharge Omnitrix after timer.
4. **Round End:** Scoreboard, rewards, and progression.

## Progression & Rewards
- **DNA Points:** Earned by eliminations, assists, survival time.
- **Unlocks:** Alien variants (color), skins, trails, emotes.
- **Ranked:** Optional Elo ladder + seasonal rewards.

## Map & Arena Design
Create 2–3 maps with varied verticality:
- **Bellwood City:** Urban rooftops, alleys, destructible props.
- **Galvan Lab:** Tech corridors, jump pads, lava pits.
- **Desert Outpost:** Wide open with dunes and caves.

## Monetization (Roblox-friendly)
- **Cosmetics Only:** Skins, trails, announcer packs.
- **Battle Pass:** Seasonal cosmetics, no power advantage.
- **Game Pass:** Extra loadout slots or custom emotes.

## Technical Notes (Roblox)
- **Server Authority:** Damage, hit validation, cooldowns.
- **Optimization:** Ability VFX LODs + pooling.
- **Anti-Exploit:** Server-side checks for speed and damage.

## MVP Scope (First Playable)
1. **Core Combat:** 5 aliens implemented with 1 map.
2. **Ability System:** Cooldowns, energy, hit detection.
3. **UI:** Transform wheel, cooldowns, scoreboard.
4. **Match Flow:** 8-player FFA, 8-minute rounds.

## Next Steps
1. Prototype ability system with 1 alien.
2. Implement transform wheel & cooldown UI.
3. Build first map with basic cover + verticality.
4. Expand to 5 aliens, then balance.
