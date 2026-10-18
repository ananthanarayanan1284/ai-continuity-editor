# Evaluation: injected contradictions

**date:** 2026-10-05 · **model:** qwen3:14b · **extraction:** v5 · **checker:** v3 · **chapters:** 24 · **test corpus check:** 438 LLM calls, 2563s · **original book check:** 282 LLM calls, 1788s

## Summary

| Measure | Value |
|---|---|
| Injected contradictions | 20 |
| Detected (recall) | 3 (15%) |
| Detected in the injected chapter itself | 3 |
| Flags raised on the test corpus | 26 |
| Flags that point at an injected contradiction (precision) | 3 (12%) |
| False alarms on harmless control edits | 0 |
| Confidence tier matches the expected tier | 67% |
| Flags on the original, unedited book (all false alarms) | 26 |

## Recall by category

| Category | Injected | Detected | Recall |
|---|---|---|---|
| characterisation | 7 | 2 | 29% |
| factual_detail | 3 | 1 | 33% |
| timeline | 4 | 0 | 0% |
| world_building | 6 | 0 | 0% |

## Precision by confidence tier

| Tier | Flags | Pointing at an injection | Precision |
|---|---|---|---|
| high | 5 | 2 | 40% |
| medium | 4 | 0 | 0% |
| low | 17 | 1 | 6% |

## Every injected contradiction

| Id | Ch | Category | Injected text | Detected | Expected tier | Flagged tier | Checker's reason |
|---|---|---|---|---|---|---|---|
| I01 | 8 | characterisation | It was true; Toto, the little white dog, had fallen down beside his little mistress. | **no** | high | - |  |
| I02 | 10 | characterisation | and even on little Toto, whose black coat now looked quite green through the glasses; and… | **no** | low | - |  |
| I03 | 11 | factual_detail | “Send me back to Kansas, where my Aunt Em and Uncle Henry, the village blacksmith, are,” … | yes | high | high | The earlier fact states that Uncle Henry was a farmer, while the new statement describes him as a village blacksmith, indicating a contradi… |
| I04 | 24 | characterisation | Aunt Em, her bright blue eyes sparkling, had just come out of the house to water the cabb… | yes | high | low | The earlier fact describes Aunt Em's eye color as 'sober gray,' while the new statement describes her eyes as 'bright blue,' indicating a c… |
| I05 | 9 | characterisation | because his head was stuffed with sawdust | yes | high | high | The earlier facts consistently state that the Scarecrow is made of straw, while the new statement claims his head is stuffed with sawdust. … |
| I06 | 11 | factual_detail | when I mentioned your golden shoes he was very much interested. | **no** | high | - |  |
| I07 | 14 | world_building | that is how it happens that we are forever, without any limit, the slaves of the owner of… | **no** | high | - |  |
| I08 | 18 | world_building | She is the most wicked of all the Witches, and rules cruelly over the Quadlings. | **no** | high | - |  |
| I09 | 11 | world_building | Dorothy and her friends were at first dazzled by the brilliancy of the wonderful City, th… | **no** | high | - |  |
| I10 | 13 | world_building | the Wicked Witch had been burned up in her own kitchen fire | **no** | high | - |  |
| I11 | 10 | world_building | while in the country of the Munchkins red was the favorite color. | **no** | high | - |  |
| I12 | 8 | timeline | “For many long years I was stuck on a pole in a cornfield | **no** | high | - |  |
| I13 | 6 | timeline | I stood rusting in the forest for only a single day, but I am not afraid so long as I hav… | **no** | high | - |  |
| I14 | 7 | characterisation | “Ah,” said the Tin Woodman sadly, “I wish I had brains to think with, for I never cared f… | **no** | high | - |  |
| I15 | 10 | characterisation | “And I want him to give me a heart, for I have plenty of courage,” said the Cowardly Lion. | **no** | high | - |  |
| I16 | 4 | factual_detail | So she told him all about Kansas, and how green and bright everything was there | **no** | medium | - |  |
| I17 | 2 | characterisation | The men, Dorothy thought, were about as old as Uncle Henry, though unlike clean-shaven Un… | **no** | high | - |  |
| I18 | 12 | world_building | But, in truth, she did not dare to strike Dorothy, although the faded mark upon her foreh… | **no** | low | - |  |
| I19 | 3 | timeline | “Because you wear silver shoes and have killed the Wicked Witch, who had ruled us for onl… | **no** | high | - |  |
| I20 | 17 | timeline | “You see, when I came to this country only last spring, it was in a balloon. | **no** | high | - |  |

## False alarms on the test corpus (23)

| Ch | Entity | New statement | Earlier fact | Tier | Checker's reason |
|---|---|---|---|---|---|
| 3 | the country | description: pretty | ch2 description: country of marvelous beauty | low | Both statements describe the country's appearance, with the first emphasizing 'marvelous beauty' and the second using 'pretty.' These are s… |
| 7 | Dorothy | wants: to reach the Emerald City | ch3 wants: to get back to Kansas | low | Earlier facts establish that Dorothy wants to return to Kansas and her aunt and uncle, while the new statement indicates she wants to reach… |
| 7 | the road | location_of_event: visible after crossing the river | ch5 location: after the forest | low | The earlier facts describe the road as being through the forest and after the forest, while the new statement describes the road as visible… |
| 8 | the little woman | ability: can enchant people and make them her slaves | ch2 ability: enslaves people | low | The new statement and earlier facts both discuss the Wicked Witch of the West's ability to enslave people, but the new statement attributes… |
| 8 | the Tin Woodman | personality: emotional and longing | ch6 personality: lacks a heart | medium | The earlier facts describe the Tin Woodman as polite, grateful, kind, careful, and lacking a heart, with no desire to kill animals. The new… |
| 9 | the poppies | effect: cause sleep | ch8 effect: causes sleep and death | low | Both statements refer to the effect of the poppies, with the earlier fact stating that they cause sleep and death, while the new statement … |
| 10 | the road | condition: smooth_and_well_paved | ch4 condition: rough | low | The earlier fact describes the road as rough, while the new statement describes it as smooth and well paved. These are contradictory descri… |
| 11 | the other Munchkin | eye_colour: green | ch4 eye_colour: painted blue by the farmer | low | The earlier facts describe the other Munchkin's eye color as blue, painted by the farmer, while the new statement describes their eye color… |
| 11 | Oz | has_rule: one visitor per day | ch10 rule: never lets anyone come into his presence | medium | The new statement introduces a new rule about Oz allowing only one visitor per day, which conflicts with the earlier rule that he 'never le… |
| 11 | the silver shoes | has_property: powerful charm | ch2 has_charm: some charm | low | The earlier fact mentions that the silver shoes have 'some charm,' while the new statement describes them as having a 'powerful charm.' Bot… |
| 11 | Oz | title: the Great and Terrible | ch2 title: the Great Wizard | low | The earlier facts refer to Oz being known as 'the Great Wizard' and 'the Great Oz,' while the new statement refers to him as 'the Great and… |
| 11 | Dorothy | wants: see Aunt Em and Uncle Henry | ch2 wants: to get back to her aunt and uncle | low | The earlier facts establish that Dorothy wants to return to Kansas and see her aunt and uncle, while the new statement shows her expressing… |
| 12 | the soldier | appearance: green whiskers | ch11 beard_colour: green | low | The earlier facts describe the soldier's beard and uniform as green, while the new statement refers to 'green whiskers.' These are closely … |
| 12 | the City of Emeralds | location: in the East | ch2 location: center of the country | medium | The earlier facts describe the Emerald City as being in the center of the country and in the land of Oz, while the new statement implies it… |
| 12 | the little woman | owns: one of the Silver Shoes | ch3 possession: silver shoes | low | The new statement mentions that the little woman owns one of the Silver Shoes, which conflicts with the earlier fact that the silver shoes … |
| 14 | the mice | count: many | ch9 number: thousands | low | The earlier fact refers to the number of mice as 'thousands,' while the new statement describes them as 'many.' Both statements refer to th… |
| 14 | the little woman | ownership_of_golden_cap: had the Golden Cap | ch12 owns: Golden Cap | medium | The earlier fact states that the Wicked Witch owns the Golden Cap, while the new statement suggests that the little woman had the Golden Ca… |
| 18 | the Scarecrow | made_of: stuffed man | ch3 made_of: straw | high | The earlier facts consistently state that the Scarecrow is made of straw, while the new statement claims he is made of a 'stuffed man', whi… |
| 18 | the Golden Cap | ability: can summon Winged Monkeys | ch12 ability: call three times upon the Winged Monkeys | low | The earlier facts describe the Golden Cap's ability as allowing three uses to command the Winged Monkeys, while the new statement only ment… |
| 18 | Dorothy | wants: to start the journey as soon as possible | ch2 wants: to get back to her aunt and uncle | low | The earlier facts all indicate that Dorothy wants to return to Kansas and her aunt and uncle, while the new statement suggests she wants to… |
| 20 | the talking lion | occupation: ladder maker | ch12 occupation: fighter | high | The earlier fact states that the talking lion is a fighter, while the new statement suggests that the talking lion is a ladder maker. These… |
| 23 | the silver shoes | origin: Dorothy | ch2 origin: the Witch of the East | high | The new statement suggests that the silver shoes belong to Dorothy, while earlier facts state that they belonged to the Witch of the East. … |
| 23 | Dorothy | emotional_state: crying | ch1 emotional_state: lonely | low | The earlier fact describes Dorothy's emotional state as 'lonely,' while the new statement describes her as 'crying.' Both are emotional sta… |