# Sonidos del pack

Generado por `scripts/build_sounds.py` (no editar a mano). Todo lo nuevo esta asignado **A CIEGAS**: nadie escucho los clips; la asignacion sale del nombre del archivo, la duracion y la analogia con el evento vanilla. Hay que probarlo en el juego.

Confianza: **N** = nombre del archivo coincide con el evento; **D** = derivado (pitch/filtro/recorte) de un clip analogo; **G** = suposicion por analogia (sin pista en el nombre)

Los eventos previos (commit e72bc24: rotura/golpe/puertas/cofres/yunque/herramientas/armaduras) no se listan aqui.
Tierra (`dirt`) y grava comparten `block.gravel.*` en vanilla.

## Mapa evento -> clips (vanilla, `assets/minecraft/sounds.json`)

| Evento | Conf. | Vol | Pitch | Clips |
|---|---|---|---|---|
| `ambient.basalt_deltas.additions` | G | 0.35 | 0.7 | ambient/cave4, ambient/cave5, ambient/cave6, ambient/cave7, ambient/cave8 |
| `ambient.cave` | G | 0.45 | - | ambient/cave1, ambient/cave2, ambient/cave3, ambient/cave4, ambient/cave5, ambient/cave6, ambient/cave7, ambient/cave8 |
| `ambient.crimson_forest.additions` | G | 0.35 | 0.7 | ambient/cave4, ambient/cave5, ambient/cave6, ambient/cave7, ambient/cave8 |
| `ambient.nether_wastes.additions` | G | 0.35 | 0.7 | ambient/cave4, ambient/cave5, ambient/cave6, ambient/cave7, ambient/cave8 |
| `ambient.soul_sand_valley.additions` | G | 0.35 | 0.7 | ambient/cave4, ambient/cave5, ambient/cave6, ambient/cave7, ambient/cave8 |
| `ambient.underwater.enter` | G | 0.5 | - | entity/splash1, entity/splash2, entity/splash3, entity/splash4, entity/splash5, entity/splash6, entity/splash7, entity/splash8 |
| `ambient.underwater.exit` | G | 0.5 | - | entity/splash1, entity/splash2, entity/splash3, entity/splash4, entity/splash5, entity/splash6, entity/splash7, entity/splash8 |
| `ambient.underwater.loop.additions` | G | 0.4 | - | block/bubble1, block/bubble2, block/bubble3 |
| `ambient.warped_forest.additions` | G | 0.35 | 0.7 | ambient/cave4, ambient/cave5, ambient/cave6, ambient/cave7, ambient/cave8 |
| `block.amethyst_block.break` | G | 0.6 | - | dig/crystal1, dig/crystal2, dig/crystal3, dig/crystal4, dig/crystal5 |
| `block.amethyst_block.chime` | G | 0.6 | - | block/crystal_chime1, block/crystal_chime2, block/crystal_chime3, block/crystal_chime4, block/crystal_chime5, block/crystal_chime6 |
| `block.amethyst_block.fall` | G | 0.42 | - | block/crystal_chime1, block/crystal_chime2, block/crystal_chime3, block/crystal_chime4, block/crystal_chime5, block/crystal_chime6 |
| `block.amethyst_block.hit` | G | 0.42 | - | block/crystal_chime1, block/crystal_chime2, block/crystal_chime3, block/crystal_chime4, block/crystal_chime5, block/crystal_chime6 |
| `block.amethyst_block.place` | G | 0.51 | - | block/crystal_chime1, block/crystal_chime2, block/crystal_chime3, block/crystal_chime4, block/crystal_chime5, block/crystal_chime6 |
| `block.amethyst_block.resonate` | G | 0.5 | 0.6 | block/crystal_chime1, block/crystal_chime2, block/crystal_chime3, block/crystal_chime4, block/crystal_chime5, block/crystal_chime6 |
| `block.amethyst_block.step` | G | 0.48 | - | block/crystal_chime1, block/crystal_chime2, block/crystal_chime3, block/crystal_chime4, block/crystal_chime5, block/crystal_chime6 |
| `block.amethyst_cluster.break` | G | 0.6 | - | dig/crystal1, dig/crystal2, dig/crystal3, dig/crystal4, dig/crystal5 |
| `block.amethyst_cluster.fall` | G | 0.5 | - | block/crystal_chime1, block/crystal_chime2, block/crystal_chime3, block/crystal_chime4, block/crystal_chime5, block/crystal_chime6 |
| `block.amethyst_cluster.hit` | G | 0.42 | - | block/crystal_chime1, block/crystal_chime2, block/crystal_chime3, block/crystal_chime4, block/crystal_chime5, block/crystal_chime6 |
| `block.amethyst_cluster.place` | G | 0.51 | - | block/crystal_chime1, block/crystal_chime2, block/crystal_chime3, block/crystal_chime4, block/crystal_chime5, block/crystal_chime6 |
| `block.amethyst_cluster.step` | G | 0.48 | - | block/crystal_chime1, block/crystal_chime2, block/crystal_chime3, block/crystal_chime4, block/crystal_chime5, block/crystal_chime6 |
| `block.ancient_debris.break` | D | 0.7 | 0.7 | block/chain_hit1, block/chain_hit2, block/chain_hit3, dig/metal_hit1 |
| `block.ancient_debris.fall` | D | 0.49 | 0.7 | block/chain_hit1, block/chain_hit2, block/chain_hit3 |
| `block.ancient_debris.hit` | D | 0.49 | 0.7 | block/chain_hit1, block/chain_hit2, block/chain_hit3 |
| `block.ancient_debris.place` | D | 0.59 | 0.7 | block/chain_hit1, block/chain_hit2, block/chain_hit3 |
| `block.ancient_debris.step` | D | 0.56 | 0.7 | block/chain_hit1, block/chain_hit2, block/chain_hit3 |
| `block.anvil.break` | G | 0.8 | - | dig/metal_slam1, item/shield_block1, item/shield_block2, item/shield_block3, item/shield_block4, item/shield_block5 |
| `block.anvil.destroy` | G | 0.8 | 0.9 | dig/metal_slam1, item/shield_block1, item/shield_block2, item/shield_block3, item/shield_block4, item/shield_block5 |
| `block.bamboo.break` | D | 0.7 | 1.4 | dig/wood_break1, dig/wood_break2 |
| `block.bamboo.fall` | D | 0.49 | 1.4 | dig/wood_hit1, dig/wood_hit2, dig/wood_hit3 |
| `block.bamboo.hit` | D | 0.49 | 1.4 | dig/wood_hit1, dig/wood_hit2, dig/wood_hit3 |
| `block.bamboo.place` | D | 0.59 | 1.4 | dig/wood_hit1, dig/wood_hit2, dig/wood_hit3 |
| `block.bamboo.step` | D | 0.56 | 1.4 | dig/wood_hit1, dig/wood_hit2, dig/wood_hit3 |
| `block.bamboo_wood.break` | D | 0.7 | 1.2 | dig/wood_break3, dig/wood_break4 |
| `block.bamboo_wood.fall` | D | 0.49 | 1.2 | step/wood1, step/wood2, step/wood3 |
| `block.bamboo_wood.hit` | D | 0.49 | 1.2 | step/wood1, step/wood2, step/wood3 |
| `block.bamboo_wood.place` | D | 0.59 | 1.2 | step/wood1, step/wood2, step/wood3 |
| `block.bamboo_wood.step` | D | 0.56 | 1.2 | step/wood1, step/wood2, step/wood3 |
| `block.basalt.break` | D | 0.8 | 0.9 | dig/stone_break1, step/stonef1, step/stonef2, step/stonef3, step/stonef4, step/stonef5, step/stonef6 |
| `block.basalt.fall` | D | 0.56 | 0.9 | step/stonef1, step/stonef2, step/stonef3, step/stonef4, step/stonef5, step/stonef6 |
| `block.basalt.hit` | D | 0.56 | 0.9 | step/stonef1, step/stonef2, step/stonef3, step/stonef4, step/stonef5, step/stonef6 |
| `block.basalt.place` | D | 0.68 | 0.9 | step/stonef1, step/stonef2, step/stonef3, step/stonef4, step/stonef5, step/stonef6 |
| `block.basalt.step` | D | 0.64 | 0.9 | step/stonef1, step/stonef2, step/stonef3, step/stonef4, step/stonef5, step/stonef6 |
| `block.beacon.activate` | G | 0.7 | - | tech/power_up1, tech/power_up2, tech/power_up3 |
| `block.beacon.ambient` | G | 0.4 | - | tech/hum1, tech/hum2, tech/hum3 |
| `block.beacon.deactivate` | G | 0.7 | - | tech/power_down1, tech/power_down2 |
| `block.beacon.power_select` | G | 0.7 | - | tech/charge1, tech/charge2 |
| `block.blastfurnace.fire_crackle` | D | 0.6 | 0.85 | block/fire_crackle1, block/fire_crackle2, block/fire_crackle3, block/fire_crackle4 |
| `block.bone_block.break` | D | 0.7 | - | dig/bone1, dig/bone2, dig/bone3, dig/bone4, dig/bone5 |
| `block.bone_block.fall` | D | 0.49 | - | dig/bone1, dig/bone2, dig/bone3, dig/bone4, dig/bone5 |
| `block.bone_block.hit` | D | 0.49 | - | dig/bone1, dig/bone2, dig/bone3, dig/bone4, dig/bone5 |
| `block.bone_block.place` | D | 0.59 | - | dig/bone1, dig/bone2, dig/bone3, dig/bone4, dig/bone5 |
| `block.bone_block.step` | D | 0.56 | - | dig/bone1, dig/bone2, dig/bone3, dig/bone4, dig/bone5 |
| `block.brewing_stand.brew` | G | 0.5 | - | block/bubble1, block/bubble2, block/bubble3, ui/bubble1, ui/bubble2, ui/bubble3 |
| `block.bubble_column.bubble_pop` | N | 0.5 | - | block/bubble1, block/bubble2, block/bubble3 |
| `block.bubble_column.upwards_ambient` | N | 0.4 | - | ambient/bubbles1, ambient/bubbles2 |
| `block.bubble_column.upwards_inside` | N | 0.4 | - | ambient/bubbles1, ambient/bubbles2 |
| `block.bubble_column.whirlpool_ambient` | D | 0.4 | 0.8 | ambient/bubbles1, ambient/bubbles2 |
| `block.bubble_column.whirlpool_inside` | D | 0.4 | 0.8 | ambient/bubbles1, ambient/bubbles2 |
| `block.campfire.crackle` | N | 0.55 | - | block/fire_crackle1, block/fire_crackle2, block/fire_crackle3, block/fire_crackle4 |
| `block.chain.break` | N | 0.6 | - | block/chain_hit1, block/chain_hit2, block/chain_hit3 |
| `block.chain.fall` | N | 0.42 | - | block/chain1, block/chain2 |
| `block.chain.hit` | N | 0.42 | - | block/chain_hit1, block/chain_hit2, block/chain_hit3 |
| `block.chain.place` | N | 0.51 | - | block/chain1, block/chain2 |
| `block.chain.step` | N | 0.48 | - | block/chain1, block/chain2 |
| `block.cherry_leaves.break` | D | 0.6 | 1.15 | step/leaves1, step/leaves2, step/leaves3 |
| `block.cherry_leaves.fall` | D | 0.42 | 1.15 | step/leaves1, step/leaves2, step/leaves3 |
| `block.cherry_leaves.hit` | D | 0.42 | 1.15 | step/leaves1, step/leaves2, step/leaves3 |
| `block.cherry_leaves.place` | D | 0.51 | 1.15 | step/leaves1, step/leaves2, step/leaves3 |
| `block.cherry_leaves.step` | D | 0.48 | 1.15 | step/leaves1, step/leaves2, step/leaves3 |
| `block.cherry_wood.break` | D | 0.7 | 1.1 | dig/wood_break6 |
| `block.cherry_wood.fall` | D | 0.49 | 1.1 | step/wood4, step/wood5, step/wood6 |
| `block.cherry_wood.hit` | D | 0.49 | 1.1 | step/wood4, step/wood5, step/wood6 |
| `block.cherry_wood.place` | D | 0.59 | 1.1 | step/wood4, step/wood5, step/wood6 |
| `block.cherry_wood.step` | D | 0.56 | 1.1 | step/wood4, step/wood5, step/wood6 |
| `block.comparator.click` | D | 0.5 | 1.3 | block/click_on1, block/click_on2, block/click_on3 |
| `block.conduit.activate` | G | 0.6 | - | tech/power_up1, tech/power_up2, tech/power_up3 |
| `block.conduit.ambient` | G | 0.4 | - | tech/force1, tech/force2, tech/force3 |
| `block.conduit.deactivate` | G | 0.6 | - | tech/power_down1, tech/power_down2 |
| `block.coral_block.break` | D | 0.7 | 1.2 | step/stonef1, step/stonef2, step/stonef3, step/stonef4, step/stonef5, step/stonef6 |
| `block.coral_block.fall` | D | 0.49 | 1.2 | step/stonef1, step/stonef2, step/stonef3, step/stonef4, step/stonef5, step/stonef6 |
| `block.coral_block.hit` | D | 0.49 | 1.2 | step/stonef1, step/stonef2, step/stonef3, step/stonef4, step/stonef5, step/stonef6 |
| `block.coral_block.place` | D | 0.59 | 1.2 | step/stonef1, step/stonef2, step/stonef3, step/stonef4, step/stonef5, step/stonef6 |
| `block.coral_block.step` | D | 0.56 | 1.2 | step/stonef1, step/stonef2, step/stonef3, step/stonef4, step/stonef5, step/stonef6 |
| `block.dispenser.dispense` | G | 0.6 | - | block/metal_click1, block/metal_click2, entity/swish_light1, entity/swish_light2, entity/swish_light3, entity/swish_light4 |
| `block.dispenser.fail` | G | 0.6 | 0.8 | block/click_off1, block/click_off2, block/click_off3, ui/error1, ui/error2 |
| `block.dispenser.launch` | G | 0.7 | - | entity/swish_heavy1, entity/swish_heavy2, entity/swish_heavy3, entity/swish_heavy4, entity/swish_heavy5, entity/swish_heavy6, entity/swish_heavy7, entity/swish_heavy8, entity/swish_heavy9 |
| `block.enchantment_table.use` | G | 0.6 | - | tech/power_up1, tech/power_up2, tech/power_up3 |
| `block.end_portal.spawn` | G | 0.8 | - | entity/explode_low1, entity/explode_low2 |
| `block.ender_chest.close` | D | 0.6 | 0.8 | tech/force1, tech/force2, tech/force3 |
| `block.ender_chest.open` | G | 0.6 | - | tech/force1, tech/force2, tech/force3 |
| `block.fire.ambient` | N | 0.5 | - | block/fire_crackle1, block/fire_crackle2, block/fire_crackle3, block/fire_crackle4 |
| `block.fire.extinguish` | D | 0.5 | - | block/extinguish1, block/extinguish2 |
| `block.furnace.fire_crackle` | N | 0.5 | - | block/fire_crackle1, block/fire_crackle2, block/fire_crackle3, block/fire_crackle4 |
| `block.gravel.break` | D | 0.7 | - | dig/gravel1, dig/gravel2, dig/gravel3, dig/gravel4, step/gravel1, step/gravel2, step/gravel3, step/gravel4, step/gravel5, step/gravel6, step/gravel7, step/gravel8 |
| `block.gravel.fall` | D | 0.49 | - | step/gravel1, step/gravel2, step/gravel3, step/gravel4, step/gravel5, step/gravel6, step/gravel7, step/gravel8 |
| `block.gravel.hit` | D | 0.49 | - | dig/gravel1, dig/gravel2, dig/gravel3, dig/gravel4 |
| `block.gravel.place` | D | 0.59 | - | dig/gravel1, dig/gravel2, dig/gravel3, dig/gravel4 |
| `block.gravel.step` | D | 0.56 | - | step/gravel1, step/gravel2, step/gravel3, step/gravel4, step/gravel5, step/gravel6, step/gravel7, step/gravel8 |
| `block.hanging_roots.break` | D | 0.5 | 0.9 | step/leaves1, step/leaves2, step/leaves3 |
| `block.hanging_roots.fall` | D | 0.35 | 0.9 | step/leaves1, step/leaves2, step/leaves3 |
| `block.hanging_roots.hit` | D | 0.35 | 0.9 | step/leaves1, step/leaves2, step/leaves3 |
| `block.hanging_roots.place` | D | 0.42 | 0.9 | step/leaves1, step/leaves2, step/leaves3 |
| `block.hanging_roots.step` | D | 0.4 | 0.9 | step/leaves1, step/leaves2, step/leaves3 |
| `block.honey_block.break` | D | 0.6 | 0.8 | block/slime1, block/slime10, block/slime11, block/slime12, block/slime2, block/slime3, block/slime4, block/slime5, block/slime6, block/slime7, block/slime8, block/slime9 |
| `block.honey_block.fall` | D | 0.42 | 0.8 | block/slime1, block/slime10, block/slime11, block/slime12, block/slime2, block/slime3, block/slime4, block/slime5, block/slime6, block/slime7, block/slime8, block/slime9 |
| `block.honey_block.hit` | D | 0.42 | 0.8 | block/slime1, block/slime10, block/slime11, block/slime12, block/slime2, block/slime3, block/slime4, block/slime5, block/slime6, block/slime7, block/slime8, block/slime9 |
| `block.honey_block.place` | D | 0.51 | 0.8 | block/slime1, block/slime10, block/slime11, block/slime12, block/slime2, block/slime3, block/slime4, block/slime5, block/slime6, block/slime7, block/slime8, block/slime9 |
| `block.honey_block.step` | D | 0.48 | 0.8 | block/slime1, block/slime10, block/slime11, block/slime12, block/slime2, block/slime3, block/slime4, block/slime5, block/slime6, block/slime7, block/slime8, block/slime9 |
| `block.large_amethyst_bud.break` | G | 0.55 | - | dig/crystal1, dig/crystal2, dig/crystal3, dig/crystal4, dig/crystal5 |
| `block.large_amethyst_bud.place` | G | 0.5 | - | block/crystal_chime1, block/crystal_chime2, block/crystal_chime3, block/crystal_chime4, block/crystal_chime5, block/crystal_chime6 |
| `block.lava.ambient` | D | 0.5 | - | ambient/lava1, ambient/lava2 |
| `block.lava.extinguish` | D | 0.6 | - | block/extinguish1, block/extinguish2 |
| `block.lava.pop` | D | 0.6 | - | block/lava_pop1, block/lava_pop2, block/lava_pop3 |
| `block.medium_amethyst_bud.break` | G | 0.55 | - | dig/crystal1, dig/crystal2, dig/crystal3, dig/crystal4, dig/crystal5 |
| `block.medium_amethyst_bud.place` | G | 0.5 | - | block/crystal_chime1, block/crystal_chime2, block/crystal_chime3, block/crystal_chime4, block/crystal_chime5, block/crystal_chime6 |
| `block.metal_pressure_plate.click_off` | D | 0.5 | 0.85 | block/metal_click1, block/metal_click2 |
| `block.metal_pressure_plate.click_on` | G | 0.6 | - | block/metal_click1, block/metal_click2 |
| `block.moss.break` | D | 0.6 | 0.8 | step/grass4, step/grass5, step/grass6 |
| `block.moss.fall` | D | 0.42 | 0.8 | step/grass4, step/grass5, step/grass6 |
| `block.moss.hit` | D | 0.42 | 0.8 | step/grass4, step/grass5, step/grass6 |
| `block.moss.place` | D | 0.51 | 0.8 | step/grass4, step/grass5, step/grass6 |
| `block.moss.step` | D | 0.48 | 0.8 | step/grass4, step/grass5, step/grass6 |
| `block.mud.break` | G | 0.6 | 0.7 | block/slime1, block/slime10, block/slime11, block/slime12, block/slime2, block/slime3, block/slime4, block/slime5, block/slime6, block/slime7, block/slime8, block/slime9 |
| `block.mud.fall` | G | 0.42 | 0.7 | block/slime1, block/slime10, block/slime11, block/slime12, block/slime2, block/slime3, block/slime4, block/slime5, block/slime6, block/slime7, block/slime8, block/slime9 |
| `block.mud.hit` | G | 0.42 | 0.7 | block/slime1, block/slime10, block/slime11, block/slime12, block/slime2, block/slime3, block/slime4, block/slime5, block/slime6, block/slime7, block/slime8, block/slime9 |
| `block.mud.place` | G | 0.51 | 0.7 | block/slime1, block/slime10, block/slime11, block/slime12, block/slime2, block/slime3, block/slime4, block/slime5, block/slime6, block/slime7, block/slime8, block/slime9 |
| `block.mud.step` | G | 0.48 | 0.7 | block/slime1, block/slime10, block/slime11, block/slime12, block/slime2, block/slime3, block/slime4, block/slime5, block/slime6, block/slime7, block/slime8, block/slime9 |
| `block.nether_bricks.break` | D | 0.75 | 0.9 | step/stonef1, step/stonef2, step/stonef3, step/stonef4, step/stonef5, step/stonef6 |
| `block.nether_bricks.fall` | D | 0.52 | 0.9 | step/stonef1, step/stonef2, step/stonef3, step/stonef4, step/stonef5, step/stonef6 |
| `block.nether_bricks.hit` | D | 0.52 | 0.9 | step/stonef1, step/stonef2, step/stonef3, step/stonef4, step/stonef5, step/stonef6 |
| `block.nether_bricks.place` | D | 0.64 | 0.9 | step/stonef1, step/stonef2, step/stonef3, step/stonef4, step/stonef5, step/stonef6 |
| `block.nether_bricks.step` | D | 0.6 | 0.9 | step/stonef1, step/stonef2, step/stonef3, step/stonef4, step/stonef5, step/stonef6 |
| `block.nether_wart.break` | D | 0.6 | 0.75 | step/leaves1, step/leaves2, step/leaves3 |
| `block.nether_wart.fall` | D | 0.42 | 0.75 | step/leaves1, step/leaves2, step/leaves3 |
| `block.nether_wart.hit` | D | 0.42 | 0.75 | step/leaves1, step/leaves2, step/leaves3 |
| `block.nether_wart.place` | D | 0.51 | 0.75 | step/leaves1, step/leaves2, step/leaves3 |
| `block.nether_wart.step` | D | 0.48 | 0.75 | step/leaves1, step/leaves2, step/leaves3 |
| `block.nether_wood.break` | D | 0.7 | 0.8 | dig/wood_break1 |
| `block.nether_wood.fall` | D | 0.49 | 0.8 | step/wood1, step/wood2 |
| `block.nether_wood.hit` | D | 0.49 | 0.8 | step/wood1, step/wood2 |
| `block.nether_wood.place` | D | 0.59 | 0.8 | step/wood1, step/wood2 |
| `block.nether_wood.step` | D | 0.56 | 0.8 | step/wood1, step/wood2 |
| `block.netherrack.break` | D | 0.75 | 0.8 | dig/stone_break1, step/stonef1, step/stonef2, step/stonef3, step/stonef4, step/stonef5, step/stonef6 |
| `block.netherrack.fall` | D | 0.52 | 0.8 | step/stonef1, step/stonef2, step/stonef3, step/stonef4, step/stonef5, step/stonef6 |
| `block.netherrack.hit` | D | 0.52 | 0.8 | step/stonef1, step/stonef2, step/stonef3, step/stonef4, step/stonef5, step/stonef6 |
| `block.netherrack.place` | D | 0.64 | 0.8 | step/stonef1, step/stonef2, step/stonef3, step/stonef4, step/stonef5, step/stonef6 |
| `block.netherrack.step` | D | 0.6 | 0.8 | step/stonef1, step/stonef2, step/stonef3, step/stonef4, step/stonef5, step/stonef6 |
| `block.nylium.break` | D | 0.65 | 0.85 | step/grass1, step/grass2, step/grass3 |
| `block.nylium.fall` | D | 0.45 | 0.85 | step/grass1, step/grass2, step/grass3 |
| `block.nylium.hit` | D | 0.45 | 0.85 | step/grass1, step/grass2, step/grass3 |
| `block.nylium.place` | D | 0.55 | 0.85 | step/grass1, step/grass2, step/grass3 |
| `block.nylium.step` | D | 0.52 | 0.85 | step/grass1, step/grass2, step/grass3 |
| `block.portal.travel` | G | 0.6 | - | tech/teleport |
| `block.powder_snow.break` | D | 0.6 | 0.85 | dig/snow1, dig/snow2, dig/snow3, dig/snow4 |
| `block.powder_snow.fall` | D | 0.42 | 0.85 | step/snow1, step/snow2, step/snow3, step/snow4, step/snow5, step/snow6, step/snow7, step/snow8 |
| `block.powder_snow.hit` | D | 0.42 | 0.85 | dig/snow1, dig/snow2, dig/snow3, dig/snow4 |
| `block.powder_snow.place` | D | 0.51 | 0.85 | dig/snow1, dig/snow2, dig/snow3, dig/snow4 |
| `block.powder_snow.step` | D | 0.48 | 0.85 | step/snow1, step/snow2, step/snow3, step/snow4, step/snow5, step/snow6, step/snow7, step/snow8 |
| `block.respawn_anchor.charge` | G | 0.7 | - | tech/charge1, tech/charge2 |
| `block.respawn_anchor.deplete` | G | 0.7 | - | tech/power_down1, tech/power_down2 |
| `block.respawn_anchor.set_spawn` | G | 0.7 | - | tech/power_up1, tech/power_up2, tech/power_up3 |
| `block.rooted_dirt.break` | D | 0.6 | 0.8 | dig/gravel1, dig/gravel2, dig/gravel3, dig/gravel4 |
| `block.rooted_dirt.fall` | D | 0.42 | 0.8 | step/gravel1, step/gravel2, step/gravel3, step/gravel4, step/gravel5, step/gravel6, step/gravel7, step/gravel8 |
| `block.rooted_dirt.hit` | D | 0.42 | 0.8 | dig/gravel1, dig/gravel2, dig/gravel3, dig/gravel4 |
| `block.rooted_dirt.place` | D | 0.51 | 0.8 | dig/gravel1, dig/gravel2, dig/gravel3, dig/gravel4 |
| `block.rooted_dirt.step` | D | 0.48 | 0.8 | step/gravel1, step/gravel2, step/gravel3, step/gravel4, step/gravel5, step/gravel6, step/gravel7, step/gravel8 |
| `block.roots.break` | D | 0.6 | 0.8 | step/grass1, step/grass2, step/grass3, step/leaves1, step/leaves2 |
| `block.roots.fall` | D | 0.42 | 0.8 | step/grass1, step/grass2, step/grass3, step/leaves1, step/leaves2 |
| `block.roots.hit` | D | 0.42 | 0.8 | step/grass1, step/grass2, step/grass3, step/leaves1, step/leaves2 |
| `block.roots.place` | D | 0.51 | 0.8 | step/grass1, step/grass2, step/grass3, step/leaves1, step/leaves2 |
| `block.roots.step` | D | 0.48 | 0.8 | step/grass1, step/grass2, step/grass3, step/leaves1, step/leaves2 |
| `block.sand.break` | N | 0.7 | - | step/sand1, step/sand2, step/sand3, step/sand4, step/sand5, step/sand6 |
| `block.sand.fall` | N | 0.49 | - | step/sand1, step/sand2, step/sand3, step/sand4, step/sand5, step/sand6 |
| `block.sand.hit` | N | 0.49 | - | step/sand1, step/sand2, step/sand3, step/sand4, step/sand5, step/sand6 |
| `block.sand.place` | N | 0.59 | - | step/sand1, step/sand2, step/sand3, step/sand4, step/sand5, step/sand6 |
| `block.sand.step` | N | 0.56 | - | step/sand1, step/sand2, step/sand3, step/sand4, step/sand5, step/sand6 |
| `block.scaffolding.break` | D | 0.7 | 1.4 | dig/wood_break5 |
| `block.scaffolding.fall` | D | 0.49 | 1.4 | dig/wood_hit4, dig/wood_hit5 |
| `block.scaffolding.hit` | D | 0.49 | 1.4 | dig/wood_hit4, dig/wood_hit5 |
| `block.scaffolding.place` | D | 0.59 | 1.4 | dig/wood_hit4, dig/wood_hit5 |
| `block.scaffolding.step` | D | 0.56 | 1.4 | dig/wood_hit4, dig/wood_hit5 |
| `block.sculk.break` | G | 0.4 | 0.6 | block/slime1, block/slime10, block/slime11, block/slime12, block/slime2, block/slime3, block/slime4, block/slime5, block/slime6, block/slime7, block/slime8, block/slime9 |
| `block.sculk.fall` | G | 0.28 | 0.6 | block/slime1, block/slime10, block/slime11, block/slime12, block/slime2, block/slime3, block/slime4, block/slime5, block/slime6, block/slime7, block/slime8, block/slime9 |
| `block.sculk.hit` | G | 0.28 | 0.6 | block/slime1, block/slime10, block/slime11, block/slime12, block/slime2, block/slime3, block/slime4, block/slime5, block/slime6, block/slime7, block/slime8, block/slime9 |
| `block.sculk.place` | G | 0.34 | 0.6 | block/slime1, block/slime10, block/slime11, block/slime12, block/slime2, block/slime3, block/slime4, block/slime5, block/slime6, block/slime7, block/slime8, block/slime9 |
| `block.sculk.step` | G | 0.32 | 0.6 | block/slime1, block/slime10, block/slime11, block/slime12, block/slime2, block/slime3, block/slime4, block/slime5, block/slime6, block/slime7, block/slime8, block/slime9 |
| `block.shulker_box.close` | D | 0.5 | 0.9 | tech/force1, tech/force2, tech/force3 |
| `block.shulker_box.open` | G | 0.5 | 1.1 | tech/force1, tech/force2, tech/force3 |
| `block.slime_block.break` | N | 0.7 | - | block/slime1, block/slime10, block/slime11, block/slime12, block/slime2, block/slime3, block/slime4, block/slime5, block/slime6, block/slime7, block/slime8, block/slime9 |
| `block.slime_block.fall` | N | 0.49 | - | block/slime1, block/slime10, block/slime11, block/slime12, block/slime2, block/slime3, block/slime4, block/slime5, block/slime6, block/slime7, block/slime8, block/slime9 |
| `block.slime_block.hit` | N | 0.49 | - | block/slime1, block/slime10, block/slime11, block/slime12, block/slime2, block/slime3, block/slime4, block/slime5, block/slime6, block/slime7, block/slime8, block/slime9 |
| `block.slime_block.place` | N | 0.59 | - | block/slime1, block/slime10, block/slime11, block/slime12, block/slime2, block/slime3, block/slime4, block/slime5, block/slime6, block/slime7, block/slime8, block/slime9 |
| `block.slime_block.step` | N | 0.56 | - | block/slime1, block/slime10, block/slime11, block/slime12, block/slime2, block/slime3, block/slime4, block/slime5, block/slime6, block/slime7, block/slime8, block/slime9 |
| `block.small_amethyst_bud.break` | G | 0.55 | - | dig/crystal1, dig/crystal2, dig/crystal3, dig/crystal4, dig/crystal5 |
| `block.small_amethyst_bud.place` | G | 0.5 | - | block/crystal_chime1, block/crystal_chime2, block/crystal_chime3, block/crystal_chime4, block/crystal_chime5, block/crystal_chime6 |
| `block.smoker.smoke` | D | 0.45 | 1.1 | block/fire_crackle1, block/fire_crackle2, block/fire_crackle3, block/fire_crackle4 |
| `block.snow.break` | N | 0.7 | - | dig/snow1, dig/snow2, dig/snow3, dig/snow4, step/snow1, step/snow2, step/snow3, step/snow4, step/snow5, step/snow6, step/snow7, step/snow8 |
| `block.snow.fall` | N | 0.49 | - | step/snow1, step/snow2, step/snow3, step/snow4, step/snow5, step/snow6, step/snow7, step/snow8 |
| `block.snow.hit` | N | 0.49 | - | dig/snow1, dig/snow2, dig/snow3, dig/snow4 |
| `block.snow.place` | N | 0.59 | - | dig/snow1, dig/snow2, dig/snow3, dig/snow4 |
| `block.snow.step` | N | 0.56 | - | step/snow1, step/snow2, step/snow3, step/snow4, step/snow5, step/snow6, step/snow7, step/snow8 |
| `block.soul_sand.break` | D | 0.7 | 0.7 | step/sand1, step/sand2, step/sand3, step/sand4, step/sand5, step/sand6 |
| `block.soul_sand.fall` | D | 0.49 | 0.7 | step/sand1, step/sand2, step/sand3, step/sand4, step/sand5, step/sand6 |
| `block.soul_sand.hit` | D | 0.49 | 0.7 | step/sand1, step/sand2, step/sand3, step/sand4, step/sand5, step/sand6 |
| `block.soul_sand.place` | D | 0.59 | 0.7 | step/sand1, step/sand2, step/sand3, step/sand4, step/sand5, step/sand6 |
| `block.soul_sand.step` | D | 0.56 | 0.7 | step/sand1, step/sand2, step/sand3, step/sand4, step/sand5, step/sand6 |
| `block.soul_soil.break` | D | 0.7 | 0.8 | step/sand1, step/sand2, step/sand3, step/sand4, step/sand5, step/sand6 |
| `block.soul_soil.fall` | D | 0.49 | 0.8 | step/sand1, step/sand2, step/sand3, step/sand4, step/sand5, step/sand6 |
| `block.soul_soil.hit` | D | 0.49 | 0.8 | step/sand1, step/sand2, step/sand3, step/sand4, step/sand5, step/sand6 |
| `block.soul_soil.place` | D | 0.59 | 0.8 | step/sand1, step/sand2, step/sand3, step/sand4, step/sand5, step/sand6 |
| `block.soul_soil.step` | D | 0.56 | 0.8 | step/sand1, step/sand2, step/sand3, step/sand4, step/sand5, step/sand6 |
| `block.stone_button.click_off` | G | 0.6 | - | block/click_off1, block/click_off2, block/click_off3 |
| `block.stone_button.click_on` | G | 0.6 | - | block/click_on1, block/click_on2, block/click_on3 |
| `block.stone_pressure_plate.click_off` | G | 0.6 | - | block/plate_off1, block/plate_off2, block/plate_off3 |
| `block.stone_pressure_plate.click_on` | G | 0.6 | - | block/plate_on1, block/plate_on2, block/plate_on3 |
| `block.sweet_berry_bush.break` | D | 0.5 | 1.1 | step/leaves4, step/leaves5 |
| `block.sweet_berry_bush.fall` | D | 0.35 | 1.1 | step/leaves4, step/leaves5 |
| `block.sweet_berry_bush.hit` | D | 0.35 | 1.1 | step/leaves4, step/leaves5 |
| `block.sweet_berry_bush.place` | D | 0.42 | 1.1 | step/leaves4, step/leaves5 |
| `block.sweet_berry_bush.step` | D | 0.4 | 1.1 | step/leaves4, step/leaves5 |
| `block.vine.break` | D | 0.5 | 0.9 | step/leaves4, step/leaves5, step/leaves6 |
| `block.vine.fall` | D | 0.35 | 0.9 | step/leaves4, step/leaves5, step/leaves6 |
| `block.vine.hit` | D | 0.35 | 0.9 | step/leaves4, step/leaves5, step/leaves6 |
| `block.vine.place` | D | 0.42 | 0.9 | step/leaves4, step/leaves5, step/leaves6 |
| `block.vine.step` | D | 0.4 | 0.9 | step/leaves4, step/leaves5, step/leaves6 |
| `block.water.ambient` | D | 0.5 | - | block/water_loop1, block/water_loop2, block/water_loop3 |
| `block.wet_grass.break` | D | 0.6 | 0.9 | step/grass4, step/grass5, step/grass6 |
| `block.wet_grass.fall` | D | 0.42 | 0.9 | step/grass4, step/grass5, step/grass6 |
| `block.wet_grass.hit` | D | 0.42 | 0.9 | step/grass4, step/grass5, step/grass6 |
| `block.wet_grass.place` | D | 0.51 | 0.9 | step/grass4, step/grass5, step/grass6 |
| `block.wet_grass.step` | D | 0.48 | 0.9 | step/grass4, step/grass5, step/grass6 |
| `block.wooden_button.click_off` | D | 0.5 | 0.85 | block/wood_click1, block/wood_click_b1, block/wood_click_b2 |
| `block.wooden_button.click_on` | G | 0.6 | - | block/wood_click1, block/wood_click_b1, block/wood_click_b2 |
| `block.wooden_pressure_plate.click_off` | D | 0.5 | 0.7 | block/wood_click1, block/wood_click_b1, block/wood_click_b2 |
| `block.wooden_pressure_plate.click_on` | D | 0.6 | 0.8 | block/wood_click1, block/wood_click_b1, block/wood_click_b2 |
| `block.wool.break` | N | 0.7 | - | dig/cloth1, dig/cloth2, step/cloth1, step/cloth2, step/cloth3, step/cloth4, step/cloth5, step/cloth6 |
| `block.wool.fall` | N | 0.49 | - | step/cloth1, step/cloth2, step/cloth3, step/cloth4, step/cloth5, step/cloth6 |
| `block.wool.hit` | N | 0.49 | - | dig/cloth1, dig/cloth2 |
| `block.wool.place` | N | 0.59 | - | dig/cloth1, dig/cloth2 |
| `block.wool.step` | N | 0.56 | - | step/cloth1, step/cloth2, step/cloth3, step/cloth4, step/cloth5, step/cloth6 |
| `entity.arrow.hit` | G | 0.6 | - | dig/wood_hit1, dig/wood_hit2, entity/chop |
| `entity.arrow.hit_player` | G | 0.6 | - | block/click_on1, block/click_on2, block/click_on3, block/crystal_chime1, block/crystal_chime2 |
| `entity.arrow.shoot` | N | 0.7 | - | entity/bow_shoot1, entity/bow_shoot2 |
| `entity.boat.paddle_water` | D | 0.4 | 1.1 | entity/splash1, entity/splash2, entity/splash3, entity/splash4, entity/splash5, entity/splash6, entity/splash7, entity/splash8 |
| `entity.experience_orb.pickup` | G | 0.5 | - | entity/xp1, entity/xp2, entity/xp3, entity/xp4, entity/xp5 |
| `entity.fishing_bobber.retrieve` | D | 0.5 | 1.1 | entity/splash1, entity/splash2, entity/splash3, entity/splash4, entity/splash5, entity/splash6, entity/splash7, entity/splash8 |
| `entity.fishing_bobber.splash` | D | 0.5 | 1.3 | entity/splash1, entity/splash2, entity/splash3, entity/splash4, entity/splash5, entity/splash6, entity/splash7, entity/splash8 |
| `entity.generic.drink` | N | 0.7 | - | entity/drink1, entity/drink2, entity/drink3 |
| `entity.generic.eat` | N | 0.8 | - | entity/eat1, entity/eat2, entity/eat3, entity/eat4, entity/eat5, entity/eat6, entity/eat7 |
| `entity.generic.explode` | N | 0.8 | - | entity/explode1, entity/explode2, entity/explode3, entity/explode4 |
| `entity.generic.splash` | N | 0.6 | - | entity/splash1, entity/splash2, entity/splash3, entity/splash4, entity/splash5, entity/splash6, entity/splash7, entity/splash8 |
| `entity.horse.armor` | N | 0.6 | - | block/chain1, block/chain2 |
| `entity.iron_golem.repair` | G | 0.7 | - | dig/metal_hit1, dig/metal_hit2, item/hammer1 |
| `entity.item.break` | G | 0.7 | 1.3 | dig/metal_hit5, item/shield_block1, item/shield_block2, item/shield_block3 |
| `entity.item.pickup` | G | 0.5 | - | entity/pickup1, entity/pickup2, entity/pickup3 |
| `entity.lightning_bolt.impact` | G | 0.8 | - | entity/explode_low1, entity/explode_low2 |
| `entity.magma_cube.squish` | D | 0.6 | 0.7 | entity/slime1, entity/slime2, entity/slime3, entity/slime4, entity/slime5, entity/slime6 |
| `entity.player.attack.crit` | G | 0.7 | 1.2 | entity/swing1, entity/swing2, entity/swing3, item/shield_block1, item/shield_block2, item/shield_block3 |
| `entity.player.attack.knockback` | G | 0.75 | - | dig/metal_slam1, entity/swish_heavy1, entity/swish_heavy2 |
| `entity.player.attack.nodamage` | G | 0.5 | 0.8 | block/click_off1, block/click_off2, block/click_off3 |
| `entity.player.attack.strong` | G | 0.75 | - | entity/swing1, entity/swing2, entity/swing3, entity/swish_heavy1, entity/swish_heavy2, entity/swish_heavy3 |
| `entity.player.attack.sweep` | G | 0.75 | - | entity/axe_swing1, entity/swish_heavy1, entity/swish_heavy2, entity/swish_heavy3, entity/swish_heavy4, entity/swish_heavy5, entity/swish_heavy6, entity/swish_heavy7, entity/swish_heavy8, entity/swish_heavy9 |
| `entity.player.attack.weak` | G | 0.7 | - | entity/dagger_swing1, entity/slice1, entity/slice2, entity/swish_light1, entity/swish_light2, entity/swish_light3, entity/swish_light4 |
| `entity.player.burp` | N | 0.7 | - | entity/burp |
| `entity.player.levelup` | G | 0.7 | - | entity/levelup |
| `entity.player.splash` | N | 0.7 | - | entity/splash1, entity/splash2, entity/splash3, entity/splash4, entity/splash5, entity/splash6, entity/splash7, entity/splash8 |
| `entity.player.splash.high_speed` | N | 0.8 | - | entity/splash_big1, entity/splash_big2, entity/splash_big3 |
| `entity.player.swim` | D | 0.4 | 1.2 | entity/splash1, entity/splash2, entity/splash3, entity/splash4, entity/splash5, entity/splash6, entity/splash7, entity/splash8 |
| `entity.skeleton.shoot` | N | 0.6 | - | entity/bow_shoot1, entity/bow_shoot2 |
| `entity.slime.attack` | D | 0.7 | 0.8 | entity/slime1, entity/slime2, entity/slime3, entity/slime4, entity/slime5, entity/slime6 |
| `entity.slime.jump` | N | 0.6 | - | entity/slime1, entity/slime2, entity/slime3, entity/slime4, entity/slime5, entity/slime6 |
| `entity.slime.jump_small` | D | 0.5 | 1.3 | entity/slime1, entity/slime2, entity/slime3, entity/slime4, entity/slime5, entity/slime6 |
| `entity.slime.squish` | N | 0.7 | - | entity/slime1, entity/slime2, entity/slime3, entity/slime4, entity/slime5, entity/slime6 |
| `entity.slime.squish_small` | D | 0.6 | 1.3 | entity/slime1, entity/slime2, entity/slime3, entity/slime4, entity/slime5, entity/slime6 |
| `entity.splash_potion.break` | D | 0.7 | - | entity/splash1, entity/splash2, entity/splash3, entity/splash4, entity/splash5, entity/splash6, entity/splash7, entity/splash8, step/glass1, step/glass2 |
| `entity.splash_potion.throw` | G | 0.6 | - | entity/swish_light1, entity/swish_light2, entity/swish_light3, entity/swish_light4 |
| `item.armor.equip_elytra` | D | 0.7 | 0.9 | armor/equip_cloth1, armor/equip_cloth2 |
| `item.armor.equip_generic` | G | 0.7 | - | armor/equip_cloth1, armor/equip_cloth2, armor/equip_leather1 |
| `item.armor.equip_leather` | N | 0.7 | - | armor/equip_leather1, armor/equip_leather2, armor/equip_leather3 |
| `item.armor.equip_turtle` | D | 0.7 | 0.8 | armor/equip_leather1, armor/equip_leather2, armor/equip_leather3 |
| `item.book.page_turn` | N | 0.7 | - | ui/page1, ui/page2, ui/page3 |
| `item.book.put` | N | 0.7 | - | ui/book_put1, ui/book_put2, ui/book_put3 |
| `item.bottle.empty` | G | 0.6 | 0.9 | block/bubble1, block/bubble2, block/bubble3 |
| `item.bottle.fill` | G | 0.6 | - | block/bubble1, block/bubble2, block/bubble3 |
| `item.bucket.empty` | G | 0.7 | - | entity/splash_big1, entity/splash_big2, entity/splash_big3 |
| `item.bucket.empty_lava` | D | 0.8 | 0.9 | block/lava_pop1, block/lava_pop2, block/lava_pop3 |
| `item.bucket.fill` | G | 0.6 | 0.9 | entity/splash1, entity/splash2, entity/splash3, entity/splash4, entity/splash5, entity/splash6, entity/splash7, entity/splash8 |
| `item.bucket.fill_lava` | D | 0.7 | - | block/lava_pop1, block/lava_pop2, block/lava_pop3 |
| `item.crossbow.hit` | G | 0.6 | - | dig/wood_hit3, entity/chop |
| `item.crossbow.loading_end` | N | 0.6 | - | item/crossbow_load3 |
| `item.crossbow.loading_middle` | N | 0.6 | - | item/crossbow_load2 |
| `item.crossbow.loading_start` | N | 0.6 | - | item/crossbow_load1 |
| `item.crossbow.quick_charge_1` | D | 0.6 | 1.2 | item/crossbow_load1 |
| `item.crossbow.quick_charge_2` | D | 0.6 | 1.2 | item/crossbow_load2 |
| `item.crossbow.quick_charge_3` | D | 0.6 | 1.2 | item/crossbow_load3 |
| `item.crossbow.shoot` | N | 0.75 | - | entity/crossbow_shoot1 |
| `item.elytra.flying` | G | 0.3 | 0.7 | entity/swish_heavy5, entity/swish_heavy6, entity/swish_heavy7, entity/swish_heavy8, entity/swish_heavy9 |
| `item.firecharge.use` | G | 0.6 | - | item/fire_use1, item/fire_use2, item/fire_use3 |
| `item.flintandsteel.use` | G | 0.5 | 1.3 | item/fire_use1, item/fire_use2, item/fire_use3 |
| `item.honey_bottle.drink` | D | 0.7 | 0.9 | entity/drink1, entity/drink2, entity/drink3 |
| `item.lodestone_compass.lock` | G | 0.6 | - | block/metal_click1, block/metal_click2 |
| `item.shield.block` | N | 0.75 | - | item/metal_pot1, item/metal_pot2, item/metal_pot3, item/shield_block1, item/shield_block2, item/shield_block3, item/shield_block4, item/shield_block5 |
| `item.shield.break` | G | 0.8 | - | dig/wood_break1, item/shield_block4, item/shield_block5 |
| `item.spyglass.stop_using` | G | 0.5 | - | ui/close1, ui/close2 |
| `item.spyglass.use` | G | 0.5 | - | ui/open1, ui/open2 |
| `item.trident.hit` | G | 0.7 | - | dig/metal_hit1, dig/metal_hit2, entity/chop |
| `item.trident.hit_ground` | G | 0.7 | - | dig/metal_hit3, dig/metal_hit4 |
| `item.trident.return` | G | 0.6 | 1.1 | entity/swish_heavy1, entity/swish_heavy2, entity/swish_heavy3 |
| `item.trident.riptide_1` | G | 0.7 | 1.0 | entity/splash1, entity/splash2, entity/swish_heavy1, entity/swish_heavy2, entity/swish_heavy3, entity/swish_heavy4, entity/swish_heavy5, entity/swish_heavy6, entity/swish_heavy7, entity/swish_heavy8, entity/swish_heavy9 |
| `item.trident.riptide_2` | G | 0.7 | 0.9 | entity/splash1, entity/splash2, entity/swish_heavy1, entity/swish_heavy2, entity/swish_heavy3, entity/swish_heavy4, entity/swish_heavy5, entity/swish_heavy6, entity/swish_heavy7, entity/swish_heavy8, entity/swish_heavy9 |
| `item.trident.riptide_3` | G | 0.7 | 0.8 | entity/splash1, entity/splash2, entity/swish_heavy1, entity/swish_heavy2, entity/swish_heavy3, entity/swish_heavy4, entity/swish_heavy5, entity/swish_heavy6, entity/swish_heavy7, entity/swish_heavy8, entity/swish_heavy9 |
| `item.trident.throw` | N | 0.7 | - | entity/spear_swing1 |
| `item.trident.thunder` | G | 0.8 | - | entity/explode_low1, entity/explode_low2 |
| `ui.cartography_table.take_result` | G | 0.6 | - | ui/page1, ui/page2, ui/page3 |
| `ui.hud.bubble_pop` | N | 0.6 | - | ui/bubble1, ui/bubble2, ui/bubble3 |
| `ui.loom.select_pattern` | G | 0.6 | - | ui/select1, ui/select2, ui/select3 |
| `ui.loom.take_result` | G | 0.6 | 1.2 | ui/select1, ui/select2, ui/select3 |
| `ui.stonecutter.select_recipe` | G | 0.5 | 0.9 | ui/select1, ui/select2, ui/select3 |
| `ui.stonecutter.take_result` | G | 0.6 | - | block/plate_on1, block/plate_on2, block/plate_on3 |
| `ui.toast.challenge_complete` | G | 0.7 | - | entity/levelup, ui/toast1, ui/toast2, ui/toast3 |
| `ui.toast.in` | G | 0.6 | - | ui/toast1, ui/toast2, ui/toast3 |
| `ui.toast.out` | G | 0.5 | - | ui/close1, ui/close2 |

## Eventos propios (`assets/drakescraft/sounds.json`, namespace `drakescraft`)

| Evento | Conf. | Vol | Pitch | Clips |
|---|---|---|---|---|
| `tech.charge` | N | 0.6 | - | tech/charge1, tech/charge2 |
| `tech.computer` | N | 0.5 | - | tech/computer1, tech/computer2, tech/computer3 |
| `tech.engine` | N | 0.5 | - | tech/engine1, tech/engine2 |
| `tech.explosion` | N | 0.7 | - | entity/explode1, entity/explode2, entity/explode_low1, entity/explode_low2 |
| `tech.force_field` | N | 0.5 | - | tech/force1, tech/force2, tech/force3 |
| `tech.gears` | G | 0.6 | - | tech/gear1, tech/gear2, tech/gear3, tech/gear4 |
| `tech.hum` | N | 0.5 | - | tech/hum1, tech/hum2, tech/hum3 |
| `tech.laser` | N | 0.5 | - | tech/laser1, tech/laser2, tech/laser3 |
| `tech.power_down` | N | 0.6 | - | tech/power_down1, tech/power_down2 |
| `tech.power_up` | N | 0.6 | - | tech/power_up1, tech/power_up2, tech/power_up3 |
| `tech.spark` | N | 0.6 | - | tech/spark1, tech/spark2, tech/spark3, tech/spark4, tech/spark5 |
| `tech.teleport` | N | 0.6 | - | tech/teleport |
| `tech.zap` | N | 0.6 | - | tech/spark1, tech/spark2, tech/spark3 |

## Fuentes (todas CC0)

- `snow`: Corsica_S (subido por qubodup) - https://opengameart.org/content/42-snow-and-gravel-footsteps - corsica_s-walking_in_snow.7z
- `fantozzi`: Fantozzi - https://opengameart.org/content/fantozzis-footsteps-grasssand-stone - Fantozzi-footsteps.7z
- `rpgpack`: artisticdude - https://opengameart.org/content/rpg-sound-pack - rpg_sound_pack.zip
- `swishes`: artisticdude - https://opengameart.org/content/swishes-sound-pack - swishes.zip
- `rpg50`: Kenney - https://opengameart.org/content/50-rpg-sound-effects - RPGsounds_Kenney.zip
- `iface`: Kenney - https://opengameart.org/content/interface-sounds - kenney_interfaceSounds.zip
- `scifi`: Kenney - https://opengameart.org/content/sci-fi-sounds - sci-fi_sounds.zip
- `digi`: Kenney - https://opengameart.org/content/63-digital-sound-effects-lasers-phasers-space-etc - Digital_SFX_Set.zip
- `crunch`: tito - https://opengameart.org/content/7-eating-crunches - crunch_-_tito.zip
- `bone`: autor indicado en la pagina - https://opengameart.org/content/deep-bone-crackbreak-sfx - deep_breaks.zip
- `water`: rubberduck (40 CC0 water / splash / slime SFX) - https://opengameart.org/comment/82442 - water-splash-slime-sfx.zip
- `splash6`: autor indicado en la pagina - https://opengameart.org/content/6-short-water-splashes - ezwa-water_splash.7z
- `ice`: IgnasD - https://opengameart.org/content/ice-breakingshattering - IceShatters_0.zip
- `medieval1`: autor indicado en la pagina (parte 1 de 2) - https://opengameart.org/content/medieval-sound-effects-weapon-textures - medieval_sfx_textures_1_of_2.7z
- `medieval2`: autor indicado en la pagina (parte 2 de 2) - https://opengameart.org/content/medieval-sound-effects-weapon-textures - medieval_sfx_textures_2_of_2.7z
- `fire`: AntumDeluge - https://opengameart.org/content/fire-crackling - fire-1_0.ogg
- `firestaff`: LEGIT Audio - https://opengameart.org/content/fire-staff-sound-effects - legit_audio_fire_staff_-_free_0.zip
- `dungeon`: autor indicado en la pagina - https://opengameart.org/content/loopable-dungeon-ambience - dungeon_ambient_1_0.ogg
- `cavern`: autor indicado en la pagina - https://opengameart.org/content/dark-cavern-ambient - dark_cavern_ambient_001.ogg, dark_cavern_ambient_002.ogg
- `elec`: Electricity Game Sound Pack - https://opengameart.org/node/150369 - chargestart.wav, charge.wav, crackleelectricityloop.wav, groundhit.wav, hit.wav, powerdown.wav, powerup.wav, recharge.wav, shieldhit.wav, snaploop.wav, teleport_1.wav, turbo.wav
- `sp03`: autor indicado en la pagina - https://opengameart.org/content/soundpack-03 - Sound03ogg.zip
- `mini15`: autor indicado en la pagina - https://opengameart.org/content/sound-effects-mini-pack15 - Sound effects Mini Pack1.5.zip

## Que falta

- Pasos de armadura (no existe evento vanilla; requeriria plugin/servidor que emita un sonido propio).
- Voz del jugador (entity.player.hurt, death, breath): no hay un pack CC0 de voces apropiado verificado.
- Lava real (block.lava.ambient/pop estan derivados de burbujas de agua con paso bajo): buscar grabacion CC0 de lava/barro.
- Tierra/dirt real: vanilla usa block.gravel.* para tierra; esta mapeado con grava+nieve (D). Falta un clip de tierra suelta.
- Hielo/escarcha dedicado: vanilla usa block.glass.* (ya mapeado antes) y block.powder_snow.*; los clips de hielo solo se usan en cristal de amatista.
- Cadena de hierro/cobre (block.iron_chain / copper_chain en versiones nuevas): solo block.chain.*.
- Engranajes reales (tech.gears usa metal chico + pestillo): falta grabacion CC0 de mecanismo/engranaje.
- Zumbido electrico sostenido (tech.hum) es el motor de la libreria Kenney; falta un hum de transformador CC0.
- Musica de discos, bloques de nota, campanas, truenos y mobs: fuera del alcance de este lote.
- Slimefun usa solo eventos vanilla (Sound.*); no hay eventos custom. Se remapearon los que mas usa (arrow.hit_player, item.break, generic.explode, lava.pop, piston, entity.player.splash, book.put/page_turn...). Eventos drakescraft:tech.* quedan listos para que un addon los emita con Bukkit playSound("drakescraft:tech.spark").
