[meta][index][font library]
meta: 格式版本、文字數量、字型高度、index offset、font library offset、字型說明
[format version: uint8_t][char cnt: uint32_t][font height: uint16_t][index offset: uint32_t][font library offset: uint32_t][desc: char x n]
index: 包含utf8轉uint32_t後的數值，以及對應到font library的offset(address)
([char idx: uint32_t][font offset: uint32_t]) x n
font library: 包含每個文字的寬度、資料長度，以及各個pixel的顏色強度(0~255)
([width: uint8_t][len: uint16_t][pixel: uint8_t x len]) x n
pixel排列方式: Left Top 逐行(橫向優先)