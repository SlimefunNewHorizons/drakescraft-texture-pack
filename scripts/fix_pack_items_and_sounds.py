#!/usr/bin/env python3
"""Repara los 41 items de herramientas restaurando definiciones de Slimefun desde 550b278,
elimina mace.json para permitir fallback nativo 1.21, corrige trident.json con modelo
especial canonico 1.21.4+, y actualiza sounds.json con replace: true en UI/interfaces."""

import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# 1. 41 herramientas a restaurar
TOOLS = [
    'diamond_spear.json', 'diamond_shovel.json', 'diamond_axe.json', 'stone_spear.json',
    'wooden_sword.json', 'diamond_pickaxe.json', 'netherite_hoe.json', 'netherite_pickaxe.json',
    'golden_pickaxe.json', 'copper_hoe.json', 'netherite_shovel.json', 'wooden_spear.json',
    'copper_sword.json', 'golden_hoe.json', 'copper_shovel.json', 'stone_pickaxe.json',
    'wooden_shovel.json', 'golden_sword.json', 'diamond_sword.json', 'iron_spear.json',
    'iron_shovel.json', 'copper_axe.json', 'iron_sword.json', 'stone_axe.json',
    'golden_spear.json', 'iron_pickaxe.json', 'iron_axe.json', 'stone_shovel.json',
    'copper_spear.json', 'stone_hoe.json', 'iron_hoe.json', 'golden_shovel.json',
    'wooden_hoe.json', 'stone_sword.json', 'diamond_hoe.json', 'golden_axe.json',
    'copper_pickaxe.json', 'wooden_axe.json', 'wooden_pickaxe.json', 'netherite_axe.json',
    'netherite_spear.json'
]

def clean_tool_data(stem, data):
    def replace_gear3d(o):
        if isinstance(o, dict):
            if o.get('type') == 'minecraft:select' and o.get('property') == 'minecraft:display_context':
                fb = o.get('fallback', {})
                if isinstance(fb, dict) and isinstance(fb.get('model'), str) and 'gear3d' in fb['model']:
                    return {'type': 'minecraft:model', 'model': f'item/{stem}'}
            if isinstance(o.get('model'), str) and 'gear3d' in o['model']:
                return {'type': 'minecraft:model', 'model': f'item/{stem}'}
            return {k: replace_gear3d(v) for k, v in o.items()}
        elif isinstance(o, list):
            return [replace_gear3d(v) for v in o]
        return o
    return replace_gear3d(data)

for tool in TOOLS:
    stem = tool.replace('.json', '')
    raw = subprocess.check_output(['git', 'show', f'550b278:assets/minecraft/items/{tool}']).decode()
    data = json.loads(raw)
    cleaned = clean_tool_data(stem, data)
    target = REPO / 'assets/minecraft/items' / tool
    target.write_text(json.dumps(cleaned, indent=2, ensure_ascii=False))

print(f"Restauradas {len(TOOLS)} herramientas limpias sin gear3d.")

# 2. Eliminar mace.json si existe en assets/minecraft/items
mace_path = REPO / 'assets/minecraft/items/mace.json'
if mace_path.exists():
    mace_path.unlink()
    print("Eliminado assets/minecraft/items/mace.json para restaurar modelo 1.21 nativo.")

# 3. Corregir trident.json
CANONICAL_TRIDENT_FALLBACK = {
    "type": "minecraft:select",
    "property": "minecraft:display_context",
    "cases": [
        {
            "model": {
                "type": "minecraft:model",
                "model": "minecraft:item/trident"
            },
            "when": [
                "gui",
                "ground",
                "fixed"
            ]
        }
    ],
    "fallback": {
        "type": "minecraft:condition",
        "property": "minecraft:using_item",
        "on_false": {
            "type": "minecraft:special",
            "base": "minecraft:item/trident_in_hand",
            "model": {
                "type": "minecraft:trident"
            }
        },
        "on_true": {
            "type": "minecraft:special",
            "base": "minecraft:item/trident_throwing",
            "model": {
                "type": "minecraft:trident"
            }
        }
    }
}

raw_trident = subprocess.check_output(['git', 'show', '550b278:assets/minecraft/items/trident.json']).decode()
trident_data = json.loads(raw_trident)

def fix_trident_fallbacks(o):
    if isinstance(o, dict):
        if o.get("model") == "minecraft:item/trident_fallback":
            return CANONICAL_TRIDENT_FALLBACK
        return {k: fix_trident_fallbacks(v) for k, v in o.items()}
    elif isinstance(o, list):
        return [fix_trident_fallbacks(v) for v in o]
    return o

trident_fixed = fix_trident_fallbacks(trident_data)
(REPO / 'assets/minecraft/items/trident.json').write_text(json.dumps(trident_fixed, indent=2, ensure_ascii=False))
print("Corregido assets/minecraft/items/trident.json con fallback especial 1.21.4+.")

# 4. Actualizar sounds.json
sounds_file = REPO / 'assets/minecraft/sounds.json'
sounds = json.loads(sounds_file.read_text())

sounds["ui.button.click"] = {
    "replace": True,
    "sounds": [
        {"name": "ui/button_click", "volume": 0.8}
    ]
}

sounds["block.chest.open"] = {
    "replace": True,
    "sounds": [
        {"name": "ui/open1", "volume": 0.7},
        {"name": "ui/open2", "volume": 0.7}
    ]
}

sounds["block.chest.close"] = {
    "replace": True,
    "sounds": [
        {"name": "ui/close1", "volume": 0.65},
        {"name": "ui/close2", "volume": 0.65}
    ]
}

sounds["block.barrel.open"] = {
    "replace": True,
    "sounds": [
        {"name": "ui/open1", "volume": 0.65},
        {"name": "ui/open2", "volume": 0.65}
    ]
}

sounds["block.barrel.close"] = {
    "replace": True,
    "sounds": [
        {"name": "ui/close1", "volume": 0.6},
        {"name": "ui/close2", "volume": 0.6}
    ]
}

sounds["block.ender_chest.open"] = {
    "replace": True,
    "sounds": [
        {"name": "tech/force1", "volume": 0.6},
        {"name": "ui/open1", "volume": 0.6}
    ]
}

sounds["block.ender_chest.close"] = {
    "replace": True,
    "sounds": [
        {"name": "tech/force1", "volume": 0.6, "pitch": 0.8},
        {"name": "ui/close1", "volume": 0.6}
    ]
}

sounds["block.shulker_box.open"] = {
    "replace": True,
    "sounds": [
        {"name": "tech/force2", "volume": 0.5, "pitch": 1.1},
        {"name": "ui/open2", "volume": 0.6}
    ]
}

sounds["block.shulker_box.close"] = {
    "replace": True,
    "sounds": [
        {"name": "tech/force2", "volume": 0.5, "pitch": 0.9},
        {"name": "ui/close2", "volume": 0.6}
    ]
}

# Sonidos de bundles/interfaces
sounds["item.bundle.insert"] = {
    "replace": True,
    "sounds": [
        {"name": "ui/select1", "volume": 0.6},
        {"name": "ui/select2", "volume": 0.6}
    ]
}
sounds["item.bundle.remove_one"] = {
    "replace": True,
    "sounds": [
        {"name": "ui/select3", "volume": 0.6},
        {"name": "ui/bubble1", "volume": 0.6}
    ]
}
sounds["item.bundle.drop_contents"] = {
    "replace": True,
    "sounds": [
        {"name": "ui/bubble2", "volume": 0.7},
        {"name": "ui/bubble3", "volume": 0.7}
    ]
}

sounds_file.write_text(json.dumps(sounds, indent=1, ensure_ascii=False))
print("Actualizado assets/minecraft/sounds.json con eventos de interfaz limpios y replace: true.")
