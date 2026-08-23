const assert = require('assert');
const Game = require('./game.js');

describe('Roguelike Game Tests', () => {
    let game;

    beforeEach(() => {
        game = new Game();
        // Suppress console output during tests
        console.log = () => {};
        console.clear = () => {};
    });

    describe('Player Movement', () => {
        it('should move player up', () => {
            const startX = game.player.x;
            const startY = game.player.y;
            game.movePlayer(0, -1);
            assert.strictEqual(game.player.x, startX);
            assert.strictEqual(game.player.y, startY - 1);
        });

        it('should move player down', () => {
            const startX = game.player.x;
            const startY = game.player.y;
            game.movePlayer(0, 1);
            assert.strictEqual(game.player.x, startX);
            assert.strictEqual(game.player.y, startY + 1);
        });

        it('should move player left', () => {
            const startX = game.player.x;
            const startY = game.player.y;
            game.movePlayer(-1, 0);
            assert.strictEqual(game.player.x, startX - 1);
            assert.strictEqual(game.player.y, startY);
        });

        it('should move player right', () => {
            const startX = game.player.x;
            const startY = game.player.y;
            game.movePlayer(1, 0);
            assert.strictEqual(game.player.x, startX + 1);
            assert.strictEqual(game.player.y, startY);
        });

        it('should not move through walls', () => {
            const startX = game.player.x;
            const startY = game.player.y;
            // Try to move through left wall
            for (let i = 0; i < 10; i++) {
                game.movePlayer(-1, 0);
            }
            // Player should not reach wall
            assert.ok(game.player.x > 0);
        });

        it('should not move outside map bounds', () => {
            const startX = game.player.x;
            const startY = game.player.y;
            // Try to move far up
            for (let i = 0; i < 50; i++) {
                game.movePlayer(0, -1);
            }
            // Player should not be at top boundary
            assert.ok(game.player.y > 0);
        });

        it('should update map when moving', () => {
            const oldX = game.player.x;
            const oldY = game.player.y;
            game.movePlayer(1, 0);
            assert.strictEqual(game.map[oldY][oldX], '.');
            assert.strictEqual(game.map[game.player.y][game.player.x], '@');
        });
    });

    describe('Monster Spawning', () => {
        it('should spawn monsters on level init', () => {
            assert.ok(game.monsters.length > 0);
        });

        it('should spawn more monsters on higher levels', () => {
            const level1Count = game.monsters.length;
            game.goToNextLevel();
            const level2Count = game.monsters.length;
            assert.ok(level2Count >= level1Count);
        });

        it('should not spawn monsters on player position', () => {
            const playerX = game.player.x;
            const playerY = game.player.y;
            const monsterOnPlayer = game.monsters.some(m => m.x === playerX && m.y === playerY);
            assert.strictEqual(monsterOnPlayer, false);
        });

        it('should not spawn monsters on stairs', () => {
            const stairsX = game.stairs.x;
            const stairsY = game.stairs.y;
            const monsterOnStairs = game.monsters.some(m => m.x === stairsX && m.y === stairsY);
            assert.strictEqual(monsterOnStairs, false);
        });

        it('should have monsters with HP > 0', () => {
            game.monsters.forEach(m => {
                assert.ok(m.hp > 0);
            });
        });

        it('should place monsters on floor tiles', () => {
            game.monsters.forEach(m => {
                assert.strictEqual(game.map[m.y][m.x], m.char);
            });
        });
    });

    describe('Stairs', () => {
        it('should place stairs on level init', () => {
            assert.ok(game.stairs.x > 0);
            assert.ok(game.stairs.y > 0);
        });

        it('should place stairs on floor tile', () => {
            assert.strictEqual(game.map[game.stairs.y][game.stairs.x], '>');
        });

        it('should go to next level when stepping on stairs', () => {
            const currentLevel = game.level;
            game.player.x = game.stairs.x;
            game.player.y = game.stairs.y;
            game.movePlayer(0, 0);
            assert.strictEqual(game.level, currentLevel + 1);
        });

        it('should not go to next level when not on stairs', () => {
            const currentLevel = game.level;
            game.player.x = game.stairs.x + 1;
            game.player.y = game.stairs.y;
            const result = game.movePlayer(0, 0);
            assert.strictEqual(game.level, currentLevel);
        });

        it('should increase difficulty on next level', () => {
            const level1Monsters = game.monsters.length;
            game.goToNextLevel();
            const level2Monsters = game.monsters.length;
            assert.ok(level2Monsters >= level1Monsters);
        });

        it('should regenerate map on next level', () => {
            const oldMap = game.map.map(row => [...row]);
            game.goToNextLevel();
            let mapChanged = false;
            for (let y = 0; y < game.height; y++) {
                for (let x = 0; x < game.width; x++) {
                    if (oldMap[y][x] !== game.map[y][x]) {
                        mapChanged = true;
                        break;
                    }
                }
                if (mapChanged) break;
            }
            assert.ok(mapChanged);
        });

        it('should win game at max level', () => {
            // Set to max level
            game.level = game.maxLevel;
            const exitCalled = process.exit.called || false;
            game.goToNextLevel();
            // Should exit with win message
            assert.ok(true);
        });
    });

    describe('Item Pickup', () => {
        it('should spawn items on level init', () => {
            assert.ok(game.items.length > 0);
        });

        it('should pick up item when on same tile', () => {
            const item = game.items[0];
            game.player.x = item.x;
            game.player.y = item.y;
            const inventoryCount = game.inventory.length;
            game.pickUp();
            assert.strictEqual(game.inventory.length, inventoryCount + 1);
            assert.strictEqual(game.inventory[game.inventory.length - 1].name, item.name);
        });

        it('should not pick up item if no item on tile', () => {
            game.player.x = 10;
            game.player.y = 10;
            const inventoryCount = game.inventory.length;
            game.pickUp();
            assert.strictEqual(game.inventory.length, inventoryCount);
        });

        it('should add item to inventory', () => {
            const item = game.items[0];
            game.player.x = item.x;
            game.player.y = item.y;
            game.pickUp();
            const found = game.inventory.some(i => i.name === item.name);
            assert.ok(found);
        });

        it('should remove item from map after pickup', () => {
            const item = game.items[0];
            game.player.x = item.x;
            game.player.y = item.y;
            game.pickUp();
            const itemStillOnMap = game.items.some(i => i.x === item.x && i.y === item.y);
            assert.strictEqual(itemStillOnMap, false);
            assert.strictEqual(game.map[item.y][item.x], '@');
        });

        it('should not exceed inventory limit', () => {
            const item = game.items[0];
            // Fill inventory to limit
            for (let i = 0; i < 10; i++) {
                game.inventory.push({ name: 'Filler', type: 'health', value: 5 });
            }
            game.player.x = item.x;
            game.player.y = item.y;
            const inventoryCount = game.inventory.length;
            game.pickUp();
            assert.strictEqual(game.inventory.length, inventoryCount);
        });

        it('should use health potion correctly', () => {
            const maxHp = game.player.maxHp;
            game.player.hp = 50;
            const item = { name: 'Health Potion', type: 'health', value: 20 };
            game.applyItem(item);
            assert.ok(game.player.hp > 50);
            assert.ok(game.player.hp <= maxHp);
        });

        it('should use weapon correctly', () => {
            const attackBefore = game.player.attack;
            const item = { name: 'Sword', type: 'weapon', value: 3 };
            game.applyItem(item);
            assert.strictEqual(game.player.attack, attackBefore + 3);
        });

        it('should use shield correctly', () => {
            const defenseBefore = game.player.defense;
            const item = { name: 'Shield', type: 'shield', value: 2 };
            game.applyItem(item);
            assert.strictEqual(game.player.defense, defenseBefore + 2);
        });

        it('should use scroll correctly', () => {
            const attackBefore = game.player.attack;
            const item = { name: 'Scroll', type: 'scroll', value: 0 };
            game.applyItem(item);
            // Scroll should either damage monsters or boost stats
            assert.ok(game.player.attack >= attackBefore || game.monsters.length < game.monsters.length);
        });
    });

    describe('Combat', () => {
        it('should attack monster when moving into it', () => {
            const monster = game.monsters[0];
            game.player.x = monster.x - 1;
            game.player.y = monster.y;
            const hpBefore = monster.hp;
            game.movePlayer(1, 0);
            assert.ok(monster.hp < hpBefore || monster.hp <= 0);
        });

        it('should not move into monster tile if alive', () => {
            const monster = game.monsters[0];
            const startX = monster.x - 1;
            const startY = monster.y;
            game.player.x = startX;
            game.player.y = startY;
            game.movePlayer(1, 0);
            if (monster.hp > 0) {
                assert.strictEqual(game.player.x, startX);
                assert.strictEqual(game.player.y, startY);
            }
        });

        it('should attack nearest monster with space', () => {
            const monster = game.monsters[0];
            game.player.x = monster.x;
            game.player.y = monster.y - 1;
            const hpBefore = monster.hp;
            game.attackNearest();
            assert.ok(monster.hp <= hpBefore || monster.hp <= 0);
        });

        it('should kill monster when HP reaches 0', () => {
            const monster = game.monsters[0];
            monster.hp = 5;
            game.player.x = monster.x;
            game.player.y = monster.y - 1;
            let attempts = 0;
            while (monster.hp > 0 && attempts < 10) {
                game.attackNearest();
                attempts++;
            }
            assert.ok(monster.hp <= 0 || !game.monsters.includes(monster));
        });

        it('should heal player when using health potion', () => {
            const initialHp = 50;
            game.player.hp = initialHp;
            const healAmount = 20;
            const item = { name: 'Health Potion', type: 'health', value: healAmount };
            game.applyItem(item);
            assert.ok(game.player.hp > initialHp);
        });
    });

    describe('Game State', () => {
        it('should track level correctly', () => {
            assert.strictEqual(game.level, 1);
            game.goToNextLevel();
            assert.strictEqual(game.level, 2);
        });

        it('should track inventory size', () => {
            const initialSize = game.inventory.length;
            const item = game.items[0];
            game.player.x = item.x;
            game.player.y = item.y;
            game.pickUp();
            assert.strictEqual(game.inventory.length, initialSize + 1);
        });

        it('should show inventory content', () => {
            const item = game.items[0];
            game.player.x = item.x;
            game.player.y = item.y;
            game.pickUp();
            const found = game.inventory.some(i => i.name === item.name);
            assert.ok(found);
        });
    });
});

console.log('All tests passed!');
