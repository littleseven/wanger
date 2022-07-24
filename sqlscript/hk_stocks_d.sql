
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for hk_stocks_d
-- ----------------------------
DROP TABLE IF EXISTS `hk_stocks_d`;
CREATE TABLE `hk_stocks_d` (
  `date` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '日期',
  `code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '代码',
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '名称',
  `sector` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '板块',
  `sp_sector` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '标普板块',
  `industry` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '行业',
  `total_cap` decimal(10,3) DEFAULT NULL COMMENT '总市值',
  `is_ss` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '是否上证成分股',
  `is_sz` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '是否深证成分股',
  `is_hs` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '是否恒生综合成分股',
  `is_spx` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '是否标普500成分股',
  `open` decimal(20,3) DEFAULT NULL COMMENT '开盘价',
  `high` decimal(20,3) DEFAULT NULL COMMENT '最高价',
  `low` decimal(20,3) DEFAULT NULL COMMENT '最低价',
  `close` decimal(20,3) DEFAULT NULL COMMENT '收盘价',
  `pre_close` decimal(20,3) DEFAULT NULL COMMENT '前一天收盘价',
  `vol` bigint DEFAULT NULL COMMENT '成交量',
  `amount` bigint DEFAULT NULL COMMENT '成交额',
  PRIMARY KEY (`date`,`code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

SET FOREIGN_KEY_CHECKS = 1;