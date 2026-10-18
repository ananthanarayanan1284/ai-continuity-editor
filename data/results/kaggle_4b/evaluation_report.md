# Evaluation: injected contradictions

**date:** 2026-10-05 · **model:** qwen3:4b-instruct · **extraction:** v5 · **checker:** v3 · **chapters:** 24 · **test corpus check:** 863 LLM calls, 4298s · **original book check:** 676 LLM calls, 3764s

## Summary

| Measure | Value |
|---|---|
| Injected contradictions | 20 |
| Detected (recall) | 1 (5%) |
| Detected in the injected chapter itself | 1 |
| Flags raised on the test corpus | 32 |
| Flags that point at an injected contradiction (precision) | 1 (3%) |
| False alarms on harmless control edits | 0 |
| Confidence tier matches the expected tier | 0% |
| Flags on the original, unedited book (all false alarms) | 29 |

## Recall by category

| Category | Injected | Detected | Recall |
|---|---|---|---|
| characterisation | 7 | 1 | 14% |
| factual_detail | 3 | 0 | 0% |
| timeline | 4 | 0 | 0% |
| world_building | 6 | 0 | 0% |

## Precision by confidence tier

| Tier | Flags | Pointing at an injection | Precision |
|---|---|---|---|
| high | 3 | 0 | 0% |
| medium | 1 | 0 | 0% |
| low | 28 | 1 | 4% |

## Every injected contradiction

| Id | Ch | Category | Injected text | Detected | Expected tier | Flagged tier | Checker's reason |
|---|---|---|---|---|---|---|---|
| I01 | 8 | characterisation | It was true; Toto, the little white dog, had fallen down beside his little mistress. | **no** | high | - |  |
| I02 | 10 | characterisation | and even on little Toto, whose black coat now looked quite green through the glasses; and… | **no** | low | - |  |
| I03 | 11 | factual_detail | “Send me back to Kansas, where my Aunt Em and Uncle Henry, the village blacksmith, are,” … | **no** | high | - |  |
| I04 | 24 | characterisation | Aunt Em, her bright blue eyes sparkling, had just come out of the house to water the cabb… | yes | high | low | The property in question is Aunt Em's occupation. Earlier, in chapter 1, it is stated that Aunt Em is 'the farmer’s wife' and specifically … |
| I05 | 9 | characterisation | because his head was stuffed with sawdust | **no** | high | - |  |
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

## False alarms on the test corpus (31)

| Ch | Entity | New statement | Earlier fact | Tier | Checker's reason |
|---|---|---|---|---|---|
| 2 | their house | appearance: not dark | ch1 appearance: one room | low | The earlier facts describe the house as having one room and being small in size. The new statement in chapter 2 adds that the house was not… |
| 2 | Dorothy | wants: to go with the Witch of the North | ch1 wants: wait calmly and see future | medium | The earlier facts establish that Dorothy wants to wait calmly and see the future, and that she resists growing gray as her surroundings do—… |
| 2 | Toto | appearance: was surprised | ch1 appearance: a little black dog, long silky hair, small black … | low | The first statement describes Toto's appearance: a little black dog with long silky hair and small black eyes. The second statement describ… |
| 3 | Dorothy | occupation: a housekeeper | ch1 occupation: little girl | low | The property in question is Dorothy's occupation. Earlier, in chapter 1, Dorothy is described as a little girl, indicating her role as a ch… |
| 3 | Toto | relationship_to_name: looked up into her face | ch1 relationship_to_dorothy: followed and lay beside Dorothy | low | The first statement establishes Toto's relationship to Dorothy as one of close companionship—following and lying beside her. The new statem… |
| 4 | the road | appearance: very uneven | ch3 appearance: painted a dainty blue color | low | The first statement describes the road's appearance as 'painted a dainty blue color,' referring to the color of the road's surface or its p… |
| 4 | the Scarecrow | personality: laughed merrily | ch3 personality: does not mind being stuffed | low | The first statement establishes that the Scarecrow does not mind being stuffed, as it is a part of his nature and he cannot get hurt. The n… |
| 4 | Dorothy | location: near a little brook | ch2 origin: dry, gray prairies | low | The property in question is Dorothy's location. Earlier, in chapter 2, it is stated that Dorothy lived in 'dry, gray prairies,' which impli… |
| 5 | the Scarecrow | occupation: made of flesh | ch3 occupation: stuffed | high | The earlier fact establishes that the Scarecrow is stuffed, a physical composition that defines his nature. The new statement claims he is … |
| 5 | the little old woman | wants: wished girl to remain and do housework | ch2 wants: to live with Dorothy | low | The earlier facts establish that the little old woman wants Dorothy to live with her and be part of her household. The new statement says s… |
| 6 | the tin man | count: one ant | ch5 count: again and again | low | The earlier fact (chapter 5) describes the tin man as expressing gratitude in a repetitive manner, using the phrase 'again and again,' indi… |
| 7 | the Lion | wants: to fight until death | ch6 wants: to have courage | low | The property in question is the Lion's desire or motivation. Earlier, in chapter 6, the Lion expresses a desire for courage, specifically a… |
| 7 | the road | origin: running through a beautiful country | ch5 origin: the forest | low | The property in question is the origin of the road. The earlier fact establishes that the road originates in the forest, while the new stat… |
| 8 | a great forest | location: behind them | ch7 location: is thick and dark | low | The earlier fact describes the forest as 'thick and dark' in terms of its appearance and atmosphere. The new statement refers to the forest… |
| 8 | a country | location: before them | ch3 origin: rich and pleasant | low | The earlier fact establishes that the country is 'rich and pleasant' and is reached after passing through 'rough and dangerous places'. The… |
| 8 | a country | origin: beckoned them on to the Emerald City | ch3 origin: rich and pleasant | low | The earlier facts describe the country's origin as being rich and pleasant, and that it is reached after passing through rough and dangerou… |
| 8 | banks of gorgeous flowers | appearance: big yellow and white and blue and purple blossoms | ch2 appearance: on every hand | low | The earlier fact describes banks of gorgeous flowers as being present 'on every hand,' indicating a widespread and abundant presence of flo… |
| 8 | banks of gorgeous flowers | appearance: great clusters of scarlet poppies | ch2 appearance: on every hand | low | The earlier fact describes banks of gorgeous flowers as being present everywhere, with a general, unspecified variety of colorful blossoms.… |
| 8 | banks of gorgeous flowers | appearance: carpeted with them | ch2 appearance: on every hand | low | The earlier fact (chapter 2) describes banks of gorgeous flowers as being 'on every hand,' indicating they are widespread and visible aroun… |
| 9 | the Munchkins | origin: all directions | ch4 origin: day before yesterday | high | The property in question is the origin of the Munchkins. Earlier, in chapter 2, it is stated that they originate from 'the land of the East… |
| 10 | Oz | location: the great Throne Room of his Palace | ch2 home: City of Emeralds | low | The property in question is location. The earlier fact establishes that Oz lives in the City of Emeralds, a specific place. The new stateme… |
| 10 | the tin man | appearance: a little man about the same size as the Munchkins | ch5 appearance: made entirely of tin, head and arms and legs join… | low | The earlier facts establish that the tin man is made entirely of tin and has a tin head with jointed limbs. The new statement describes him… |
| 11 | the Lion | wants: never have courage | ch6 wants: to have courage | low | The property is the Lion's desire or possession of courage. Earlier, the Lion expresses a wish to have courage; in the new statement, he de… |
| 16 | Oz | occupation: tinsmith | ch2 occupation: Great Wizard | high | The property in question is Oz's occupation. Earlier facts establish that Oz is the Great Wizard, with multiple references in chapters 2 an… |
| 17 | Oz | home: the Emerald City | ch11 location: located in the middle of the City | low | The earlier fact establishes that the Palace of Oz is located in the middle of the City, indicating a specific location within the city. Th… |
| 18 | the Winged Monkeys | count: a band | ch14 count: two | low | The first statement establishes that there are one or three Winged Monkeys in chapter 14, and a second specifies two Monkeys carrying Dorot… |
| 21 | a great forest | appearance: bigger and older than any they had ever seen | ch4 appearance: trees grew so big and close together | low | The first statement describes the appearance of the forest in terms of tree size and density—trees growing so big and close together that t… |
| 21 | the Scarecrow | personality: gloomy, cautious | ch4 personality: laughed merrily | low | The earlier facts establish the Scarecrow's personality as one of comfort with being stuffed (fact 1), discomfort with being a fool (fact 2… |
| 22 | the King Crow | origin: ruler of the Winged Monkeys | ch14 home: lived in the forest near Gayelette’s palace | low | The property in question is the King Crow's relationship to the Winged Monkeys. Earlier, in chapter 14, it is stated that the King Crow's g… |
| 23 | the Winged Monkeys | home: land of the Winkies | ch14 origin: from the Land of the West | low | The property in question is the origin or home of the Winged Monkeys. Earlier facts establish that the Winged Monkeys originated in or are … |
| 23 | the Lion | occupation: is big and shaggy | ch8 occupation: stepped upon the raft | low | The earlier fact establishes that the Lion's occupation is related to stepping upon a raft, which is a physical action in a scene involving… |