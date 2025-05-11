-- phpMyAdmin SQL Dump
-- version 4.8.5
-- https://www.phpmyadmin.net/
--
-- 主机： localhost
-- 生成日期： 2025-05-11 10:25:23
-- 服务器版本： 8.0.12
-- PHP 版本： 7.3.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 数据库： `elderly_care_system`
--

-- --------------------------------------------------------

--
-- 表的结构 `area_codes`
--

CREATE TABLE `area_codes` (
  `id` int(11) NOT NULL,
  `region` varchar(50) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `province` varchar(50) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `city` varchar(50) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `code` int(11) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- 转存表中的数据 `area_codes`
--

INSERT INTO `area_codes` (`id`, `region`, `province`, `city`, `code`, `created_at`) VALUES
(1, '华北', '北京', NULL, 911, '2025-05-11 01:23:55'),
(2, '华北', '天津', NULL, 923, '2025-05-11 01:23:55'),
(3, '华北', '河北', NULL, 920, '2025-05-11 01:23:55'),
(4, '华北', '山西', NULL, 929, '2025-05-11 01:23:55'),
(5, '华北', '内蒙古', NULL, 905, '2025-05-11 01:23:55'),
(6, '东北', '辽宁', NULL, 907, '2025-05-11 01:23:55'),
(7, '东北', '吉林', NULL, 922, '2025-05-11 01:23:55'),
(8, '东北', '黑龙江', NULL, 921, '2025-05-11 01:23:55'),
(9, '华东', '上海', NULL, 910, '2025-05-11 01:23:55'),
(10, '华东', '江苏', NULL, 916, '2025-05-11 01:23:55'),
(11, '华东', '浙江', NULL, 917, '2025-05-11 01:23:55'),
(12, '华东', '安徽', NULL, 928, '2025-05-11 01:23:55'),
(13, '华东', '福建', NULL, 909, '2025-05-11 01:23:55'),
(14, '华东', '江西', NULL, 903, '2025-05-11 01:23:55'),
(15, '华东', '山东', NULL, 901, '2025-05-11 01:23:55'),
(16, '华中', '河南', NULL, 927, '2025-05-11 01:23:55'),
(17, '华中', '湖北', NULL, 906, '2025-05-11 01:23:55'),
(18, '华中', '湖南', NULL, 908, '2025-05-11 01:23:55'),
(19, '华南', '广东', NULL, 913, '2025-05-11 01:23:55'),
(20, '华南', '广西', NULL, 912, '2025-05-11 01:23:55'),
(21, '华南', '海南', NULL, 930, '2025-05-11 01:23:55'),
(22, '西南', '重庆', NULL, 904, '2025-05-11 01:23:55'),
(23, '西南', '四川', NULL, 914, '2025-05-11 01:23:55'),
(24, '西南', '贵州', NULL, 902, '2025-05-11 01:23:55'),
(25, '西南', '云南', NULL, 915, '2025-05-11 01:23:55'),
(26, '西南', '西藏', NULL, 932, '2025-05-11 01:23:55'),
(27, '西北', '陕西', NULL, 924, '2025-05-11 01:23:55'),
(28, '西北', '甘肃', NULL, 925, '2025-05-11 01:23:55'),
(29, '西北', '青海', NULL, 918, '2025-05-11 01:23:55'),
(30, '西北', '宁夏', NULL, 919, '2025-05-11 01:23:55'),
(31, '西北', '新疆', NULL, 926, '2025-05-11 01:23:55'),
(32, '港澳台', '台湾', NULL, 931, '2025-05-11 01:23:55'),
(33, '港澳台', '香港', NULL, 933, '2025-05-11 01:23:55'),
(34, '港澳台', '澳门', NULL, 934, '2025-05-11 01:23:55'),
(35, '华北', '北京', '东城区', 1001, '2025-05-11 01:23:55'),
(36, '华北', '北京', '西城区', 1002, '2025-05-11 01:23:55'),
(37, '华北', '北京', '朝阳区', 1003, '2025-05-11 01:23:55'),
(38, '华北', '北京', '海淀区', 1004, '2025-05-11 01:23:55'),
(39, '华北', '北京', '丰台区', 1005, '2025-05-11 01:23:55'),
(40, '华北', '北京', '石景山区', 1006, '2025-05-11 01:23:55'),
(41, '华北', '北京', '通州区', 1007, '2025-05-11 01:23:55'),
(42, '华北', '北京', '昌平区', 1008, '2025-05-11 01:23:55'),
(43, '华北', '天津', '和平区', 2001, '2025-05-11 01:23:55'),
(44, '华北', '天津', '河东区', 2002, '2025-05-11 01:23:55'),
(45, '华北', '天津', '河西区', 2003, '2025-05-11 01:23:55'),
(46, '华北', '天津', '南开区', 2004, '2025-05-11 01:23:55'),
(47, '华北', '天津', '河北区', 2005, '2025-05-11 01:23:55'),
(48, '华北', '天津', '红桥区', 2006, '2025-05-11 01:23:55'),
(49, '华北', '天津', '滨海新区', 2007, '2025-05-11 01:23:55'),
(50, '华北', '河北', '石家庄', 327, '2025-05-11 01:23:55'),
(51, '华北', '河北', '唐山', 329, '2025-05-11 01:23:55'),
(52, '华北', '河北', '秦皇岛', 325, '2025-05-11 01:23:55'),
(53, '华北', '河北', '邯郸', 330, '2025-05-11 01:23:55'),
(54, '华北', '河北', '邢台', 326, '2025-05-11 01:23:55'),
(55, '华北', '河北', '保定', 304, '2025-05-11 01:23:55'),
(56, '华北', '河北', '张家口', 331, '2025-05-11 01:23:55'),
(57, '华北', '河北', '承德', 306, '2025-05-11 01:23:55'),
(58, '华北', '河北', '沧州', 305, '2025-05-11 01:23:55'),
(59, '华北', '河北', '廊坊', 307, '2025-05-11 01:23:55'),
(60, '华北', '河北', '衡水', 332, '2025-05-11 01:23:55'),
(61, '华北', '山西', '太原', 214, '2025-05-11 01:23:55'),
(62, '华北', '山西', '大同', 217, '2025-05-11 01:23:55'),
(63, '华北', '山西', '阳泉', 215, '2025-05-11 01:23:55'),
(64, '华北', '山西', '长治', 209, '2025-05-11 01:23:55'),
(65, '华北', '山西', '晋城', 205, '2025-05-11 01:23:55'),
(66, '华北', '山西', '朔州', 213, '2025-05-11 01:23:55'),
(67, '华北', '山西', '晋中', 206, '2025-05-11 01:23:55'),
(68, '华北', '山西', '运城', 216, '2025-05-11 01:23:55'),
(69, '华北', '山西', '忻州', 212, '2025-05-11 01:23:55'),
(70, '华北', '山西', '临汾', 211, '2025-05-11 01:23:55'),
(71, '华北', '山西', '吕梁', 210, '2025-05-11 01:23:55'),
(72, '华北', '内蒙古', '呼和浩特', 167, '2025-05-11 01:23:55'),
(73, '华北', '内蒙古', '包头', 169, '2025-05-11 01:23:55'),
(74, '华北', '内蒙古', '乌海', 164, '2025-05-11 01:23:55'),
(75, '华北', '内蒙古', '赤峰', 158, '2025-05-11 01:23:55'),
(76, '华北', '内蒙古', '通辽', 161, '2025-05-11 01:23:55'),
(77, '华北', '内蒙古', '鄂尔多斯', 168, '2025-05-11 01:23:55'),
(78, '华北', '内蒙古', '呼伦贝尔', 166, '2025-05-11 01:23:55'),
(79, '华北', '内蒙古', '巴彦淖尔', 162, '2025-05-11 01:23:55'),
(80, '华北', '内蒙古', '乌兰察布', 163, '2025-05-11 01:23:55'),
(81, '华北', '内蒙古', '兴安盟', 160, '2025-05-11 01:23:55'),
(82, '华北', '内蒙古', '锡林郭勒盟', 165, '2025-05-11 01:23:55'),
(83, '华北', '内蒙古', '阿拉善盟', 159, '2025-05-11 01:23:55'),
(84, '东北', '辽宁', '沈阳', 153, '2025-05-11 01:23:55'),
(85, '东北', '辽宁', '大连', 155, '2025-05-11 01:23:55'),
(86, '东北', '辽宁', '鞍山', 151, '2025-05-11 01:23:55'),
(87, '东北', '辽宁', '抚顺', 152, '2025-05-11 01:23:55'),
(88, '东北', '辽宁', '本溪', 145, '2025-05-11 01:23:55'),
(89, '东北', '辽宁', '丹东', 144, '2025-05-11 01:23:55'),
(90, '东北', '辽宁', '锦州', 146, '2025-05-11 01:23:55'),
(91, '东北', '辽宁', '营口', 156, '2025-05-11 01:23:55'),
(92, '东北', '辽宁', '阜新', 150, '2025-05-11 01:23:55'),
(93, '东北', '辽宁', '辽阳', 148, '2025-05-11 01:23:55'),
(94, '东北', '辽宁', '盘锦', 149, '2025-05-11 01:23:55'),
(95, '东北', '辽宁', '铁岭', 154, '2025-05-11 01:23:55'),
(96, '东北', '辽宁', '朝阳', 147, '2025-05-11 01:23:55'),
(97, '东北', '辽宁', '葫芦岛', 157, '2025-05-11 01:23:55'),
(98, '东北', '吉林', '长春', 40, '2025-05-11 01:23:55'),
(99, '东北', '吉林', '吉林市', 38, '2025-05-11 01:23:55'),
(100, '东北', '吉林', '四平', 43, '2025-05-11 01:23:55'),
(101, '东北', '吉林', '辽源', 41, '2025-05-11 01:23:55'),
(102, '东北', '吉林', '通化', 45, '2025-05-11 01:23:55'),
(103, '东北', '吉林', '白山', 42, '2025-05-11 01:23:55'),
(104, '东北', '吉林', '松原', 44, '2025-05-11 01:23:55'),
(105, '东北', '吉林', '白城', 39, '2025-05-11 01:23:55'),
(106, '东北', '吉林', '延边', 47, '2025-05-11 01:23:55'),
(107, '东北', '吉林', '延吉', 46, '2025-05-11 01:23:55'),
(108, '东北', '黑龙江', '哈尔滨', 335, '2025-05-11 01:23:55'),
(109, '东北', '黑龙江', '齐齐哈尔', 337, '2025-05-11 01:23:55'),
(110, '东北', '黑龙江', '鸡西', 333, '2025-05-11 01:23:55'),
(111, '东北', '黑龙江', '鹤岗', 344, '2025-05-11 01:23:55'),
(112, '东北', '黑龙江', '双鸭山', 340, '2025-05-11 01:23:55'),
(113, '东北', '黑龙江', '大庆', 342, '2025-05-11 01:23:55'),
(114, '东北', '黑龙江', '伊春', 341, '2025-05-11 01:23:55'),
(115, '东北', '黑龙江', '佳木斯', 334, '2025-05-11 01:23:55'),
(116, '东北', '黑龙江', '七台河', 338, '2025-05-11 01:23:55'),
(117, '东北', '黑龙江', '牡丹江', 336, '2025-05-11 01:23:55'),
(118, '东北', '黑龙江', '黑河', 345, '2025-05-11 01:23:55'),
(119, '东北', '黑龙江', '绥化', 339, '2025-05-11 01:23:55'),
(120, '东北', '黑龙江', '大兴安岭', 343, '2025-05-11 01:23:55'),
(121, '华东', '上海', '黄浦区', 3001, '2025-05-11 01:23:55'),
(122, '华东', '上海', '徐汇区', 3002, '2025-05-11 01:23:55'),
(123, '华东', '上海', '长宁区', 3003, '2025-05-11 01:23:55'),
(124, '华东', '上海', '静安区', 3004, '2025-05-11 01:23:55'),
(125, '华东', '上海', '普陀区', 3005, '2025-05-11 01:23:55'),
(126, '华东', '上海', '虹口区', 3006, '2025-05-11 01:23:55'),
(127, '华东', '上海', '杨浦区', 3007, '2025-05-11 01:23:55'),
(128, '华东', '上海', '浦东新区', 3008, '2025-05-11 01:23:55'),
(129, '华东', '江苏', '南京', 55, '2025-05-11 01:23:55'),
(130, '华东', '江苏', '无锡', 62, '2025-05-11 01:23:55'),
(131, '华东', '江苏', '徐州', 58, '2025-05-11 01:23:55'),
(132, '华东', '江苏', '常州', 54, '2025-05-11 01:23:55'),
(133, '华东', '江苏', '苏州', 59, '2025-05-11 01:23:55'),
(134, '华东', '江苏', '南通', 56, '2025-05-11 01:23:55'),
(135, '华东', '江苏', '连云港', 57, '2025-05-11 01:23:55'),
(136, '华东', '江苏', '淮安', 53, '2025-05-11 01:23:55'),
(137, '华东', '江苏', '盐城', 63, '2025-05-11 01:23:55'),
(138, '华东', '江苏', '扬州', 64, '2025-05-11 01:23:55'),
(139, '华东', '江苏', '镇江', 65, '2025-05-11 01:23:55'),
(140, '华东', '江苏', '泰州', 61, '2025-05-11 01:23:55'),
(141, '华东', '江苏', '宿迁', 60, '2025-05-11 01:23:55'),
(142, '华东', '浙江', '杭州', 280, '2025-05-11 01:23:55'),
(143, '华东', '浙江', '宁波', 276, '2025-05-11 01:23:55'),
(144, '华东', '浙江', '温州', 278, '2025-05-11 01:23:55'),
(145, '华东', '浙江', '嘉兴', 273, '2025-05-11 01:23:55'),
(146, '华东', '浙江', '湖州', 282, '2025-05-11 01:23:55'),
(147, '华东', '浙江', '绍兴', 277, '2025-05-11 01:23:55'),
(148, '华东', '浙江', '金华', 272, '2025-05-11 01:23:55'),
(149, '华东', '浙江', '衢州', 274, '2025-05-11 01:23:55'),
(150, '华东', '浙江', '舟山', 281, '2025-05-11 01:23:55'),
(151, '华东', '浙江', '台州', 279, '2025-05-11 01:23:55'),
(152, '华东', '浙江', '丽水', 275, '2025-05-11 01:23:55'),
(153, '华东', '安徽', '合肥', 142, '2025-05-11 01:23:55'),
(154, '华东', '安徽', '芜湖', 139, '2025-05-11 01:23:55'),
(155, '华东', '安徽', '蚌埠', 141, '2025-05-11 01:23:55'),
(156, '华东', '安徽', '淮南', 133, '2025-05-11 01:23:55'),
(157, '华东', '安徽', '马鞍山', 134, '2025-05-11 01:23:55'),
(158, '华东', '安徽', '淮北', 127, '2025-05-11 01:23:55'),
(159, '华东', '安徽', '铜陵', 138, '2025-05-11 01:23:55'),
(160, '华东', '安徽', '安庆', 128, '2025-05-11 01:23:55'),
(161, '华东', '安徽', '黄山', 132, '2025-05-11 01:23:55'),
(162, '华东', '安徽', '滁州', 131, '2025-05-11 01:23:55'),
(163, '华东', '安徽', '阜阳', 140, '2025-05-11 01:23:55'),
(164, '华东', '安徽', '宿州', 137, '2025-05-11 01:23:55'),
(165, '华东', '安徽', '六安', 135, '2025-05-11 01:23:55'),
(166, '华东', '安徽', '亳州', 143, '2025-05-11 01:23:55'),
(167, '华东', '安徽', '池州', 130, '2025-05-11 01:23:55'),
(168, '华东', '安徽', '宣城', 136, '2025-05-11 01:23:55'),
(169, '华东', '福建', '福州', 81, '2025-05-11 01:23:55'),
(170, '华东', '福建', '厦门', 70, '2025-05-11 01:23:55'),
(171, '华东', '福建', '莆田', 48, '2025-05-11 01:23:55'),
(172, '华东', '福建', '三明', 66, '2025-05-11 01:23:55'),
(173, '华东', '福建', '泉州', 52, '2025-05-11 01:23:55'),
(174, '华东', '福建', '漳州', 80, '2025-05-11 01:23:55'),
(175, '华东', '福建', '南平', 49, '2025-05-11 01:23:55'),
(176, '华东', '福建', '龙岩', 50, '2025-05-11 01:23:55'),
(177, '华东', '福建', '宁德', 51, '2025-05-11 01:23:55'),
(178, '华东', '江西', '南昌', 72, '2025-05-11 01:23:55'),
(179, '华东', '江西', '景德镇', 69, '2025-05-11 01:23:55'),
(180, '华东', '江西', '萍乡', 71, '2025-05-11 01:23:55'),
(181, '华东', '江西', '九江', 67, '2025-05-11 01:23:55'),
(182, '华东', '江西', '新余', 73, '2025-05-11 01:23:55'),
(183, '华东', '江西', '鹰潭', 76, '2025-05-11 01:23:55'),
(184, '华东', '江西', '赣州', 77, '2025-05-11 01:23:55'),
(185, '华东', '江西', '吉安', 68, '2025-05-11 01:23:55'),
(186, '华东', '江西', '宜春', 75, '2025-05-11 01:23:55'),
(187, '华东', '江西', '抚州', 78, '2025-05-11 01:23:55'),
(188, '华东', '江西', '上饶', 74, '2025-05-11 01:23:55'),
(189, '华东', '山东', '济南', 196, '2025-05-11 01:23:55'),
(190, '华东', '山东', '青岛', 202, '2025-05-11 01:23:55'),
(191, '华东', '山东', '淄博', 207, '2025-05-11 01:23:55'),
(192, '华东', '山东', '枣庄', 221, '2025-05-11 01:23:55'),
(193, '华东', '山东', '东营', 220, '2025-05-11 01:23:55'),
(194, '华东', '山东', '烟台', 219, '2025-05-11 01:23:55'),
(195, '华东', '山东', '潍坊', 204, '2025-05-11 01:23:55'),
(196, '华东', '山东', '济宁', 197, '2025-05-11 01:23:55'),
(197, '华东', '山东', '泰安', 208, '2025-05-11 01:23:55'),
(198, '华东', '山东', '威海', 218, '2025-05-11 01:23:55'),
(199, '华东', '山东', '日照', 203, '2025-05-11 01:23:55'),
(200, '华东', '山东', '临沂', 201, '2025-05-11 01:23:55'),
(201, '华东', '山东', '德州', 200, '2025-05-11 01:23:55'),
(202, '华东', '山东', '聊城', 199, '2025-05-11 01:23:55'),
(203, '华东', '山东', '滨州', 223, '2025-05-11 01:23:55'),
(204, '华东', '山东', '菏泽', 222, '2025-05-11 01:23:55'),
(205, '华中', '河南', '郑州', 322, '2025-05-11 01:23:55'),
(206, '华中', '河南', '开封', 310, '2025-05-11 01:23:55'),
(207, '华中', '河南', '洛阳', 311, '2025-05-11 01:23:55'),
(208, '华中', '河南', '平顶山', 313, '2025-05-11 01:23:55'),
(209, '华中', '河南', '安阳', 309, '2025-05-11 01:23:55'),
(210, '华中', '河南', '鹤壁', 323, '2025-05-11 01:23:55'),
(211, '华中', '河南', '新乡', 317, '2025-05-11 01:23:55'),
(212, '华中', '河南', '焦作', 308, '2025-05-11 01:23:55'),
(213, '华中', '河南', '濮阳', 316, '2025-05-11 01:23:55'),
(214, '华中', '河南', '许昌', 319, '2025-05-11 01:23:55'),
(215, '华中', '河南', '漯河', 312, '2025-05-11 01:23:55'),
(216, '华中', '河南', '三门峡', 321, '2025-05-11 01:23:55'),
(217, '华中', '河南', '南阳', 315, '2025-05-11 01:23:55'),
(218, '华中', '河南', '商丘', 320, '2025-05-11 01:23:55'),
(219, '华中', '河南', '信阳', 318, '2025-05-11 01:23:55'),
(220, '华中', '河南', '周口', 324, '2025-05-11 01:23:55'),
(221, '华中', '河南', '驻马店', 314, '2025-05-11 01:23:55'),
(222, '华中', '河南', '济源', 476, '2025-05-11 01:23:55'),
(223, '华中', '湖北', '武汉', 371, '2025-05-11 01:23:55'),
(224, '华中', '湖北', '黄石', 348, '2025-05-11 01:23:55'),
(225, '华中', '湖北', '十堰', 369, '2025-05-11 01:23:55'),
(226, '华中', '湖北', '宜昌', 376, '2025-05-11 01:23:55'),
(227, '华中', '湖北', '襄阳', 370, '2025-05-11 01:23:55'),
(228, '华中', '湖北', '鄂州', 377, '2025-05-11 01:23:55'),
(229, '华中', '湖北', '荆门', 346, '2025-05-11 01:23:55'),
(230, '华中', '湖北', '孝感', 365, '2025-05-11 01:23:55'),
(231, '华中', '湖北', '荆州', 347, '2025-05-11 01:23:55'),
(232, '华中', '湖北', '黄冈', 349, '2025-05-11 01:23:55'),
(233, '华中', '湖北', '咸宁', 375, '2025-05-11 01:23:55'),
(234, '华中', '湖北', '随州', 367, '2025-05-11 01:23:55'),
(235, '华中', '湖北', '恩施', 366, '2025-05-11 01:23:55'),
(236, '华中', '湖北', '仙桃', 372, '2025-05-11 01:23:55'),
(237, '华中', '湖北', '潜江', 364, '2025-05-11 01:23:55'),
(238, '华中', '湖北', '天门', 373, '2025-05-11 01:23:55'),
(239, '华中', '湖北', '神农架', 368, '2025-05-11 01:23:55'),
(240, '华中', '湖南', '长沙', 352, '2025-05-11 01:23:55'),
(241, '华中', '湖南', '株洲', 363, '2025-05-11 01:23:55'),
(242, '华中', '湖南', '湘潭', 356, '2025-05-11 01:23:55'),
(243, '华中', '湖南', '衡阳', 360, '2025-05-11 01:23:55'),
(244, '华中', '湖南', '邵阳', 355, '2025-05-11 01:23:55'),
(245, '华中', '湖南', '岳阳', 361, '2025-05-11 01:23:55'),
(246, '华中', '湖南', '常德', 351, '2025-05-11 01:23:55'),
(247, '华中', '湖南', '张家界', 358, '2025-05-11 01:23:55'),
(248, '华中', '湖南', '益阳', 359, '2025-05-11 01:23:55'),
(249, '华中', '湖南', '郴州', 353, '2025-05-11 01:23:55'),
(250, '华中', '湖南', '永州', 362, '2025-05-11 01:23:55'),
(251, '华中', '湖南', '怀化', 350, '2025-05-11 01:23:55'),
(252, '华中', '湖南', '娄底', 354, '2025-05-11 01:23:55'),
(253, '华中', '湖南', '湘西', 357, '2025-05-11 01:23:55'),
(254, '华南', '广东', '广州', 84, '2025-05-11 01:23:55'),
(255, '华南', '广东', '深圳', 93, '2025-05-11 01:23:55'),
(256, '华南', '广东', '珠海', 113, '2025-05-11 01:23:55'),
(257, '华南', '广东', '汕头', 91, '2025-05-11 01:23:55'),
(258, '华南', '广东', '佛山', 90, '2025-05-11 01:23:55'),
(259, '华南', '广东', '韶关', 94, '2025-05-11 01:23:55'),
(260, '华南', '广东', '湛江', 110, '2025-05-11 01:23:55'),
(261, '华南', '广东', '肇庆', 114, '2025-05-11 01:23:55'),
(262, '华南', '广东', '江门', 82, '2025-05-11 01:23:55'),
(263, '华南', '广东', '茂名', 86, '2025-05-11 01:23:55'),
(264, '华南', '广东', '惠州', 117, '2025-05-11 01:23:55'),
(265, '华南', '广东', '梅州', 88, '2025-05-11 01:23:55'),
(266, '华南', '广东', '汕尾', 92, '2025-05-11 01:23:55'),
(267, '华南', '广东', '河源', 115, '2025-05-11 01:23:55'),
(268, '华南', '广东', '阳江', 109, '2025-05-11 01:23:55'),
(269, '华南', '广东', '清远', 89, '2025-05-11 01:23:55'),
(270, '华南', '广东', '东莞', 116, '2025-05-11 01:23:55'),
(271, '华南', '广东', '中山', 112, '2025-05-11 01:23:55'),
(272, '华南', '广东', '潮州', 85, '2025-05-11 01:23:55'),
(273, '华南', '广东', '揭阳', 83, '2025-05-11 01:23:55'),
(274, '华南', '广东', '云浮', 111, '2025-05-11 01:23:55'),
(275, '华南', '广西', '南宁', 99, '2025-05-11 01:23:55'),
(276, '华南', '广西', '柳州', 101, '2025-05-11 01:23:55'),
(277, '华南', '广西', '桂林', 95, '2025-05-11 01:23:55'),
(278, '华南', '广西', '梧州', 103, '2025-05-11 01:23:55'),
(279, '华南', '广西', '北海', 104, '2025-05-11 01:23:55'),
(280, '华南', '广西', '防城港', 98, '2025-05-11 01:23:55'),
(281, '华南', '广西', '钦州', 102, '2025-05-11 01:23:55'),
(282, '华南', '广西', '贵港', 96, '2025-05-11 01:23:55'),
(283, '华南', '广西', '玉林', 105, '2025-05-11 01:23:55'),
(284, '华南', '广西', '百色', 108, '2025-05-11 01:23:55'),
(285, '华南', '广西', '贺州', 107, '2025-05-11 01:23:55'),
(286, '华南', '广西', '河池', 106, '2025-05-11 01:23:55'),
(287, '华南', '广西', '来宾', 100, '2025-05-11 01:23:55'),
(288, '华南', '广西', '崇左', 478, '2025-05-11 01:23:55'),
(289, '华南', '海南', '海口', 302, '2025-05-11 01:23:55'),
(290, '华南', '海南', '三亚', 298, '2025-05-11 01:23:55'),
(291, '华南', '海南', '三沙', 122, '2025-05-11 01:23:55'),
(292, '华南', '海南', '儋州', 303, '2025-05-11 01:23:55'),
(293, '华南', '海南', '五指山', 300, '2025-05-11 01:23:55'),
(294, '华南', '海南', '琼海', 297, '2025-05-11 01:23:55'),
(295, '华南', '海南', '文昌', 299, '2025-05-11 01:23:55'),
(296, '华南', '海南', '万宁', 301, '2025-05-11 01:23:55'),
(297, '华南', '海南', '东方', 296, '2025-05-11 01:23:55'),
(298, '华南', '海南', '定安县', 484, '2025-05-11 01:23:55'),
(299, '华南', '海南', '屯昌县', 485, '2025-05-11 01:23:55'),
(300, '华南', '海南', '陵水黎族自治县', 486, '2025-05-11 01:23:55'),
(301, '华南', '海南', '澄迈县', 487, '2025-05-11 01:23:55'),
(302, '华南', '海南', '保亭黎族苗族自治县', 488, '2025-05-11 01:23:55'),
(303, '华南', '海南', '琼中黎族苗族自治县', 489, '2025-05-11 01:23:55'),
(304, '华南', '海南', '乐东黎族自治县', 490, '2025-05-11 01:23:55'),
(305, '华南', '海南', '临高县', 491, '2025-05-11 01:23:55'),
(306, '华南', '海南', '昌江黎族自治县', 492, '2025-05-11 01:23:55'),
(307, '华南', '海南', '白沙黎族自治县', 493, '2025-05-11 01:23:55'),
(308, '西南', '重庆', '渝中区', 4001, '2025-05-11 01:23:55'),
(309, '西南', '重庆', '江北区', 4002, '2025-05-11 01:23:55'),
(310, '西南', '重庆', '南岸区', 4003, '2025-05-11 01:23:55'),
(311, '西南', '重庆', '沙坪坝区', 4004, '2025-05-11 01:23:55'),
(312, '西南', '重庆', '九龙坡区', 4005, '2025-05-11 01:23:55'),
(313, '西南', '重庆', '大渡口区', 4006, '2025-05-11 01:23:55'),
(314, '西南', '四川', '成都', 226, '2025-05-11 01:23:55'),
(315, '西南', '四川', '绵阳', 229, '2025-05-11 01:23:55'),
(316, '西南', '四川', '自贡', 253, '2025-05-11 01:23:55'),
(317, '西南', '四川', '攀枝花', 230, '2025-05-11 01:23:55'),
(318, '西南', '四川', '泸州', 234, '2025-05-11 01:23:55'),
(319, '西南', '四川', '德阳', 232, '2025-05-11 01:23:55'),
(320, '西南', '四川', '广元', 225, '2025-05-11 01:23:55'),
(321, '西南', '四川', '遂宁', 237, '2025-05-11 01:23:55'),
(322, '西南', '四川', '内江', 235, '2025-05-11 01:23:55'),
(323, '西南', '四川', '乐山', 233, '2025-05-11 01:23:55'),
(324, '西南', '四川', '南充', 231, '2025-05-11 01:23:55'),
(325, '西南', '四川', '宜宾', 254, '2025-05-11 01:23:55'),
(326, '西南', '四川', '广安', 224, '2025-05-11 01:23:55'),
(327, '西南', '四川', '达州', 250, '2025-05-11 01:23:55'),
(328, '西南', '四川', '眉山', 227, '2025-05-11 01:23:55'),
(329, '西南', '四川', '雅安', 251, '2025-05-11 01:23:55'),
(330, '西南', '四川', '巴中', 247, '2025-05-11 01:23:55'),
(331, '西南', '四川', '资阳', 238, '2025-05-11 01:23:55'),
(332, '西南', '四川', '阿坝', 252, '2025-05-11 01:23:55'),
(333, '西南', '四川', '甘孜', 236, '2025-05-11 01:23:55'),
(334, '西南', '四川', '凉山', 228, '2025-05-11 01:23:55'),
(335, '西南', '贵州', '贵阳', 118, '2025-05-11 01:23:55'),
(336, '西南', '贵州', '六盘水', 120, '2025-05-11 01:23:55'),
(337, '西南', '贵州', '遵义', 126, '2025-05-11 01:23:55'),
(338, '西南', '贵州', '安顺', 119, '2025-05-11 01:23:55'),
(339, '西南', '贵州', '毕节', 124, '2025-05-11 01:23:55'),
(340, '西南', '贵州', '铜仁', 125, '2025-05-11 01:23:55'),
(341, '西南', '贵州', '黔西南', 123, '2025-05-11 01:23:55'),
(342, '西南', '贵州', '黔东南', 122, '2025-05-11 01:23:55'),
(343, '西南', '贵州', '黔南', 121, '2025-05-11 01:23:55'),
(344, '西南', '云南', '昆明', 284, '2025-05-11 01:23:55'),
(345, '西南', '云南', '曲靖', 288, '2025-05-11 01:23:55'),
(346, '西南', '云南', '玉溪', 295, '2025-05-11 01:23:55'),
(347, '西南', '云南', '保山', 289, '2025-05-11 01:23:55'),
(348, '西南', '云南', '昭通', 294, '2025-05-11 01:23:55'),
(349, '西南', '云南', '丽江', 285, '2025-05-11 01:23:55'),
(350, '西南', '云南', '普洱', 290, '2025-05-11 01:23:55'),
(351, '西南', '云南', '临沧', 287, '2025-05-11 01:23:55'),
(352, '西南', '云南', '楚雄', 283, '2025-05-11 01:23:55'),
(353, '西南', '云南', '红河', 293, '2025-05-11 01:23:55'),
(354, '西南', '云南', '文山', 291, '2025-05-11 01:23:55'),
(355, '西南', '云南', '西双版纳', 483, '2025-05-11 01:23:55'),
(356, '西南', '云南', '大理', 292, '2025-05-11 01:23:55'),
(357, '西南', '云南', '德宏', 286, '2025-05-11 01:23:55'),
(358, '西南', '云南', '怒江', 481, '2025-05-11 01:23:55'),
(359, '西南', '云南', '迪庆', 482, '2025-05-11 01:23:55'),
(360, '西南', '西藏', '拉萨', 269, '2025-05-11 01:23:55'),
(361, '西南', '西藏', '日喀则', 271, '2025-05-11 01:23:55'),
(362, '西南', '西藏', '昌都', 480, '2025-05-11 01:23:55'),
(363, '西南', '西藏', '林芝', 270, '2025-05-11 01:23:55'),
(364, '西南', '西藏', '山南', 497, '2025-05-11 01:23:55'),
(365, '西南', '西藏', '那曲', 268, '2025-05-11 01:23:55'),
(366, '西南', '西藏', '阿里', 498, '2025-05-11 01:23:55'),
(367, '西北', '陕西', '西安', 244, '2025-05-11 01:23:55'),
(368, '西北', '陕西', '铜川', 242, '2025-05-11 01:23:55'),
(369, '西北', '陕西', '宝鸡', 239, '2025-05-11 01:23:55'),
(370, '西北', '陕西', '咸阳', 245, '2025-05-11 01:23:55'),
(371, '西北', '陕西', '渭南', 243, '2025-05-11 01:23:55'),
(372, '西北', '陕西', '延安', 246, '2025-05-11 01:23:55'),
(373, '西北', '陕西', '汉中', 248, '2025-05-11 01:23:55'),
(374, '西北', '陕西', '榆林', 249, '2025-05-11 01:23:55'),
(375, '西北', '陕西', '安康', 240, '2025-05-11 01:23:55'),
(376, '西北', '陕西', '商洛', 241, '2025-05-11 01:23:55'),
(377, '西北', '甘肃', '兰州', 258, '2025-05-11 01:23:55'),
(378, '西北', '甘肃', '嘉峪关', 257, '2025-05-11 01:23:55'),
(379, '西北', '甘肃', '金昌', 256, '2025-05-11 01:23:55'),
(380, '西北', '甘肃', '白银', 267, '2025-05-11 01:23:55'),
(381, '西北', '甘肃', '天水', 265, '2025-05-11 01:23:55'),
(382, '西北', '甘肃', '武威', 264, '2025-05-11 01:23:55'),
(383, '西北', '甘肃', '张掖', 266, '2025-05-11 01:23:55'),
(384, '西北', '甘肃', '平凉', 260, '2025-05-11 01:23:55'),
(385, '西北', '甘肃', '酒泉', 255, '2025-05-11 01:23:55'),
(386, '西北', '甘肃', '庆阳', 262, '2025-05-11 01:23:55'),
(387, '西北', '甘肃', '定西', 263, '2025-05-11 01:23:55'),
(388, '西北', '甘肃', '陇南', 259, '2025-05-11 01:23:55'),
(389, '西北', '甘肃', '临夏', 261, '2025-05-11 01:23:55'),
(390, '西北', '甘肃', '甘南', 477, '2025-05-11 01:23:55'),
(391, '西北', '青海', '西宁', 175, '2025-05-11 01:23:55'),
(392, '西北', '青海', '海东', 176, '2025-05-11 01:23:55'),
(393, '西北', '青海', '海北', 494, '2025-05-11 01:23:55'),
(394, '西北', '青海', '黄南', 495, '2025-05-11 01:23:55'),
(395, '西北', '青海', '海南', 479, '2025-05-11 01:23:55'),
(396, '西北', '青海', '果洛', 496, '2025-05-11 01:23:55'),
(397, '西北', '青海', '玉树', 178, '2025-05-11 01:23:55'),
(398, '西北', '青海', '海西', 177, '2025-05-11 01:23:55'),
(399, '西北', '宁夏', '银川', 174, '2025-05-11 01:23:55'),
(400, '西北', '宁夏', '石嘴山', 171, '2025-05-11 01:23:55'),
(401, '西北', '宁夏', '吴忠', 172, '2025-05-11 01:23:55'),
(402, '西北', '宁夏', '固原', 170, '2025-05-11 01:23:55'),
(403, '西北', '宁夏', '中卫', 173, '2025-05-11 01:23:55'),
(404, '西北', '新疆', '乌鲁木齐', 192, '2025-05-11 01:23:55'),
(405, '西北', '新疆', '克拉玛依', 184, '2025-05-11 01:23:55'),
(406, '西北', '新疆', '吐鲁番', 190, '2025-05-11 01:23:55'),
(407, '西北', '新疆', '哈密', 179, '2025-05-11 01:23:55'),
(408, '西北', '新疆', '昌吉', 181, '2025-05-11 01:23:55'),
(409, '西北', '新疆', '博尔塔拉', 180, '2025-05-11 01:23:55'),
(410, '西北', '新疆', '巴音郭楞', 191, '2025-05-11 01:23:55'),
(411, '西北', '新疆', '阿克苏', 185, '2025-05-11 01:23:55'),
(412, '西北', '新疆', '克孜勒苏柯尔克孜', 186, '2025-05-11 01:23:55'),
(413, '西北', '新疆', '喀什', 183, '2025-05-11 01:23:55'),
(414, '西北', '新疆', '和田', 195, '2025-05-11 01:23:55'),
(415, '西北', '新疆', '伊犁', 193, '2025-05-11 01:23:55'),
(416, '西北', '新疆', '塔城', 188, '2025-05-11 01:23:55'),
(417, '西北', '新疆', '阿勒泰', 182, '2025-05-11 01:23:55'),
(418, '西北', '新疆', '石河子', 187, '2025-05-11 01:23:55'),
(419, '西北', '新疆', '阿拉尔', 499, '2025-05-11 01:23:55'),
(420, '西北', '新疆', '图木舒克', 500, '2025-05-11 01:23:55'),
(421, '西北', '新疆', '五家渠', 189, '2025-05-11 01:23:55');

-- --------------------------------------------------------

--
-- 表的结构 `baidu_index_trends`
--

CREATE TABLE `baidu_index_trends` (
  `id` int(11) NOT NULL,
  `date` date NOT NULL,
  `index_value` int(11) NOT NULL,
  `area` varchar(50) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `keyword` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- 表的结构 `cookies`
--

CREATE TABLE `cookies` (
  `id` int(11) NOT NULL,
  `username` varchar(50) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `cookie_data` json NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- 转存表中的数据 `cookies`
--

INSERT INTO `cookies` (`id`, `username`, `cookie_data`, `created_at`) VALUES
(1, '18584855132', '{\"RT\": \"\\\"z=1&dm=baidu.com&si=868deeb8-e4da-4bc8-9362-4b942fa602cb&ss=m9yd25ov&sl=3&tt=8ao&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf\\\"\", \"XFI\": \"18da2270-22b1-11f0-a549-59a26aaf6a4e\", \"XFT\": \"/FKuhJ8NaogYP8gmF4ENhBouEtOA3CtOjM0p1+Cy8fM=\", \"XFCS\": \"243C610E9E3053A80A3C04707ACD3299F7AA6FCBE21C1A657A74656D0B840CC1\", \"BDUSS\": \"UF6UU1Sd0dsWGlYWmswTTYtYnVaTkpxVVk4VG5Tem1RYjhPcmg5SDloTmJoVFJvSVFBQUFBJCQAAAAAAQAAAAEAAAAVucsnQW1kb27YvEN5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFv4DGhb-AxoO\", \"ab_sr\": \"1.0.1_MzRiZmUxNWViZTc5Y2FjNjI0MWIxYTBlYjg2NmIxM2NiNDhlMzIwZGVjYWI4Y2FjNWI1MmRiYmYyYzhhMTQyNTQ1ZGIyYzY3NzllN2JmYTgwM2EyMWRiODE3ZDM4MThiYzA5MTRmMWZlOTNlYTM0MjNhZDEwNzM2NzQxNTZmMGQ4MzRmZjQ5NGQxZTMyMzAzOWVmZDZiYzc3OThhMzRiZQ==\", \"ppfuid\": \"FOCoIC3q5fKa8fgJnwzbE67EJ49BGJeplOzf+4l4EOvDuu2RXBRv6R3A1AZMa49I27C0gDDLrJyxcIIeAeEhD8JYsoLTpBiaCXhLqvzbzmvy3SeAW17tKgNq/Xx+RgOdb8TWCFe62MVrDTY6lMf2GrfqL8c87KLF2qFER3obJGmxOaJD7Qr04D9rET96PX99GEimjy3MrXEpSuItnI4KD2P5vWa8VVdqKPLBckQ0Wyrci+eNtO+sUfx41sINYk+wnxP1CK1TUkCIVuuFLG7q3zGkP+rnwsdG6xtmvJvAJOHGgLbz7OSojK1zRbqBESR5Pdk2R9IA3lxxOVzA+Iw1TWLSgWjlFVG9Xmh1+20oPSbrzvDjYtVPmZ+9/6evcXmhcO1Y58MgLozKnaQIaLfWRHYJbniad6MOTaDR3XV1dTJNjGCbnYWN73rxtX036bU+lqe3DyQvjDt6TZ+KXd2BKtnTNS/pLMWceus0e757/UN2nsqw9F4aiTP2No0RRtYGAAv3LCf1Y7/fHL3PTSf9vid/u2VLX4h1nBtx8EF07eCMhWVv+2qjbPV7ZhXk3reaWRFEeso3s/Kc9n/UXtUfNU1sHiCdbrCW5yYsuSM9SPGDZsl7FhTAKw7qIu38vFZiq+DRc8Vbf7jOiN9xPe0lOdZHUhGHZ82rL5jTCsILwcRVCndrarbwmu7G154MpYiKmTXZkqV7Alo4QZzicdyMbWvwvmR2/m//YVTM8qeZWgDSHjDmtehgLWM45zARbPujeqU0T92Gmgs89l2htrSKIVH643AT57ChWkPiYU253bxJ3m/v5NOzfJUm6z9wbA91OA/nMoLYJp0NJVb5maqgv5dImdyxYIjA1uSy2hfTFv/d3cnXH4nh+maaicAPllDg5eQg3PzwS3cxyDdVnXm0S3SzlDBMoJre+/eEVILl9qfJG4J1XxaCSXJyWOxW8eEyKFRUJsY13C1vsjCpm8CVES1YaiglkVXf9JFlGDT9U1DMCZgnBfRZSLUD0OQvZht1R/MUcjdNssK4n8T/CBddBwUyci33bLRLxtuUeiWfm1d+b2nRqUTK6NqmhPLvsfMNGXY5cw7t/lpvUTLIOZZV4ISnUwo07XURRBo18y8vw5JYLi2wPs57Eh/DALGu/t2TjxI3zzhoI6py6AKLxXifk4igQD90ocWvR4zXnx/3Vf6FcZVouo5DCvlQhjRhvpItmpX9rNeekRxrKhekOFe8ArBFVDtu1KaJzjx51nTN1+xVI8c7otOFm3py1Y+wrt2CfI5v5JSd2kRNZE7s6bQrA5yMI31SfUDgxDrsd6lPtUU=\", \"BAIDUID\": \"987E8D630BC22D575A30C0B2D4D08B59:FG=1\", \"CPID_212\": \"60952149\", \"CPTK_212\": \"1683877274\", \"HMACCOUNT\": \"BA1468BD5A04977B\", \"SIGNIN_UC\": \"70a2711cf1d3d9b1a82d2f87d633bd8a04956929244WE9R9JmtRqkcy9fAk3b6VuJEyncj%2BO8dO28kvhM%2B4vu2sdAYA%2FTb2XXcucd74T4xXV14lRpcAczoLiteEXTJ4RiiIqDYGqliyLTvhANlIUBPkIhV6cL3Ah9Z3sedYZeD8Ui5ZhXPjAoLlw3zyeL6fjWsp3qOzaJj2Qh%2FJzicto0VdPYlSLnH%2FdBNWGUUwKYjiRcvtLtoJQ0GO9Wd1kpVoG3Qx%2BoLUaaFtPeHina9E3ikU58ctNpznS752GmLYPV2KgP8WSITOx%2BJ0Zv9MG3svO2w7IvOysEP%2B6myfDVNCvY%3D51304657544743187946220778800073\", \"__cas__rn__\": \"495692924\", \"BAIDUID_BFESS\": \"987E8D630BC22D575A30C0B2D4D08B59:FG=1\", \"__cas__id__212\": \"60952149\", \"__cas__st__212\": \"915e2a70fe7e5d6fccead7f4b8cef60c8d5e3c162917f01cab78bd53a91fb00c5ef1f0949a700a1aa71f64c2\", \"Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc\": \"1745680438\", \"Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc\": \"1745680477\"}', '2025-04-26 15:14:37'),
(4, 'admin', '{\"RT\": \"\\\"z=1&dm=baidu.com&si=868deeb8-e4da-4bc8-9362-4b942fa602cb&ss=m9yd25ov&sl=3&tt=8ao&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf\\\"\", \"XFI\": \"18da2270-22b1-11f0-a549-59a26aaf6a4e\", \"XFT\": \"/FKuhJ8NaogYP8gmF4ENhBouEtOA3CtOjM0p1+Cy8fM=\", \"XFCS\": \"243C610E9E3053A80A3C04707ACD3299F7AA6FCBE21C1A657A74656D0B840CC1\", \"BDUSS\": \"UF6UU1Sd0dsWGlYWmswTTYtYnVaTkpxVVk4VG5Tem1RYjhPcmg5SDloTmJoVFJvSVFBQUFBJCQAAAAAAQAAAAEAAAAVucsnQW1kb27YvEN5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFv4DGhb-AxoO\", \"ab_sr\": \"1.0.1_MzRiZmUxNWViZTc5Y2FjNjI0MWIxYTBlYjg2NmIxM2NiNDhlMzIwZGVjYWI4Y2FjNWI1MmRiYmYyYzhhMTQyNTQ1ZGIyYzY3NzllN2JmYTgwM2EyMWRiODE3ZDM4MThiYzA5MTRmMWZlOTNlYTM0MjNhZDEwNzM2NzQxNTZmMGQ4MzRmZjQ5NGQxZTMyMzAzOWVmZDZiYzc3OThhMzRiZQ==\", \"ppfuid\": \"FOCoIC3q5fKa8fgJnwzbE67EJ49BGJeplOzf+4l4EOvDuu2RXBRv6R3A1AZMa49I27C0gDDLrJyxcIIeAeEhD8JYsoLTpBiaCXhLqvzbzmvy3SeAW17tKgNq/Xx+RgOdb8TWCFe62MVrDTY6lMf2GrfqL8c87KLF2qFER3obJGmxOaJD7Qr04D9rET96PX99GEimjy3MrXEpSuItnI4KD2P5vWa8VVdqKPLBckQ0Wyrci+eNtO+sUfx41sINYk+wnxP1CK1TUkCIVuuFLG7q3zGkP+rnwsdG6xtmvJvAJOHGgLbz7OSojK1zRbqBESR5Pdk2R9IA3lxxOVzA+Iw1TWLSgWjlFVG9Xmh1+20oPSbrzvDjYtVPmZ+9/6evcXmhcO1Y58MgLozKnaQIaLfWRHYJbniad6MOTaDR3XV1dTJNjGCbnYWN73rxtX036bU+lqe3DyQvjDt6TZ+KXd2BKtnTNS/pLMWceus0e757/UN2nsqw9F4aiTP2No0RRtYGAAv3LCf1Y7/fHL3PTSf9vid/u2VLX4h1nBtx8EF07eCMhWVv+2qjbPV7ZhXk3reaWRFEeso3s/Kc9n/UXtUfNU1sHiCdbrCW5yYsuSM9SPGDZsl7FhTAKw7qIu38vFZiq+DRc8Vbf7jOiN9xPe0lOdZHUhGHZ82rL5jTCsILwcRVCndrarbwmu7G154MpYiKmTXZkqV7Alo4QZzicdyMbWvwvmR2/m//YVTM8qeZWgDSHjDmtehgLWM45zARbPujeqU0T92Gmgs89l2htrSKIVH643AT57ChWkPiYU253bxJ3m/v5NOzfJUm6z9wbA91OA/nMoLYJp0NJVb5maqgv5dImdyxYIjA1uSy2hfTFv/d3cnXH4nh+maaicAPllDg5eQg3PzwS3cxyDdVnXm0S3SzlDBMoJre+/eEVILl9qfJG4J1XxaCSXJyWOxW8eEyKFRUJsY13C1vsjCpm8CVES1YaiglkVXf9JFlGDT9U1DMCZgnBfRZSLUD0OQvZht1R/MUcjdNssK4n8T/CBddBwUyci33bLRLxtuUeiWfm1d+b2nRqUTK6NqmhPLvsfMNGXY5cw7t/lpvUTLIOZZV4ISnUwo07XURRBo18y8vw5JYLi2wPs57Eh/DALGu/t2TjxI3zzhoI6py6AKLxXifk4igQD90ocWvR4zXnx/3Vf6FcZVouo5DCvlQhjRhvpItmpX9rNeekRxrKhekOFe8ArBFVDtu1KaJzjx51nTN1+xVI8c7otOFm3py1Y+wrt2CfI5v5JSd2kRNZE7s6bQrA5yMI31SfUDgxDrsd6lPtUU=\", \"BAIDUID\": \"987E8D630BC22D575A30C0B2D4D08B59:FG=1\", \"CPID_212\": \"60952149\", \"CPTK_212\": \"1683877274\", \"HMACCOUNT\": \"BA1468BD5A04977B\", \"SIGNIN_UC\": \"70a2711cf1d3d9b1a82d2f87d633bd8a04956929244WE9R9JmtRqkcy9fAk3b6VuJEyncj%2BO8dO28kvhM%2B4vu2sdAYA%2FTb2XXcucd74T4xXV14lRpcAczoLiteEXTJ4RiiIqDYGqliyLTvhANlIUBPkIhV6cL3Ah9Z3sedYZeD8Ui5ZhXPjAoLlw3zyeL6fjWsp3qOzaJj2Qh%2FJzicto0VdPYlSLnH%2FdBNWGUUwKYjiRcvtLtoJQ0GO9Wd1kpVoG3Qx%2BoLUaaFtPeHina9E3ikU58ctNpznS752GmLYPV2KgP8WSITOx%2BJ0Zv9MG3svO2w7IvOysEP%2B6myfDVNCvY%3D51304657544743187946220778800073\", \"__cas__rn__\": \"495692924\", \"BAIDUID_BFESS\": \"987E8D630BC22D575A30C0B2D4D08B59:FG=1\", \"__cas__id__212\": \"60952149\", \"__cas__st__212\": \"915e2a70fe7e5d6fccead7f4b8cef60c8d5e3c162917f01cab78bd53a91fb00c5ef1f0949a700a1aa71f64c2\", \"Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc\": \"1745680438\", \"Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc\": \"1745680477\"}', '2025-04-26 15:14:43'),
(2, '18781162981', '{\"RT\": \"\\\"z=1&dm=baidu.com&si=71fca3b2-b66d-40bb-b9df-d49c9f6c9ad9&ss=m8iq35ql&sl=2&tt=4oj&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=goq\\\"\", \"BDUSS\": \"pHTjJJV3RhTWVpNy1vR0dBUXJHZEp2NDZwaWtxR0FSMjlxSGoweFNPV1E0QVJvSVFBQUFBJCQAAAAAAQAAAAEAAAB5rwGWSm9zZW5DeQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJBT3WeQU91ncH\", \"ab_sr\": \"1.0.1_Yzc4NjFkOTQ4MTY5NTAzYTM5YmUzNDRlMTJkMTM4NTEzNmMzY2UwOWY1YWZkNmI5ZDM5ZDhkMjUxMjgyZmQ3OTUzZjIzYmJiZWUzMWFhMTBhMzUyY2UyZGYwYTc0NmJkZDM2MjllYzU3NmMxZWVjYmFkYzJlODQ3MDkxNTFiZjBmZmQ1NWFlYWUyNzJkMThjY2FmOWY1ZWE0ZGFiZDkxYw==\", \"ppfuid\": \"FOCoIC3q5fKa8fgJnwzbE67EJ49BGJeplOzf+4l4EOvDuu2RXBRv6R3A1AZMa49I27C0gDDLrJyxcIIeAeEhD8JYsoLTpBiaCXhLqvzbzmvy3SeAW17tKgNq/Xx+RgOdb8TWCFe62MVrDTY6lMf2GrfqL8c87KLF2qFER3obJGmxOaJD7Qr04D9rET96PX99GEimjy3MrXEpSuItnI4KD2P5vWa8VVdqKPLBckQ0WyrgwNSQKKIDdXA6eDfuiw2FJ3ZBF1sLBqLP1Lik2nWCKk4sXpnMWzrlcw817brPPlfGgLbz7OSojK1zRbqBESR5Pdk2R9IA3lxxOVzA+Iw1TWLSgWjlFVG9Xmh1+20oPSbrzvDjYtVPmZ+9/6evcXmhcO1Y58MgLozKnaQIaLfWRHYJbniad6MOTaDR3XV1dTLxUSUZS0ReZYJMPG6nCsxNJlhI2UyeJA6QroZFMelR7tnTNS/pLMWceus0e757/UMPmrThfasmhDJrMFcBfoSrAAv3LCf1Y7/fHL3PTSf9vid/u2VLX4h1nBtx8EF07eCMhWVv+2qjbPV7ZhXk3reaWRFEeso3s/Kc9n/UXtUfNU1sHiCdbrCW5yYsuSM9SPGDZsl7FhTAKw7qIu38vFZiq+DRc8Vbf7jOiN9xPe0lOdZHUhGHZ82rL5jTCsILwcRVCndrarbwmu7G154MpYiKmTXZkqV7Alo4QZzicdyMbWvwvmR2/m//YVTM8qeZWgDSHjDmtehgLWM45zARbPujeqU0T92Gmgs89l2htrSKIVfEFzbtyzdes2f7rMR3DsT9s7hrTTo9fvI0eb7EXkrl28iVHWejeTfeu67KQzKLYpdImdyxYIjA1uSy2hfTFv/d3cnXH4nh+maaicAPllDg7JjsxZAfQoVAycJHizlQ5d34k8SzMID0x3kxnXwHfxXvz6DS3RnKydYTBUIWPYKJAEFefnSer1pU55Mw3PEJuMbPGO6Per4Y9UBohIIx5FdrGRChHnhPuJeIKACPXiVuli9ItRLEkdb1mLxNHAk3uJy88YX/Rf/sKUjR12zxRTDxxJNDJS+Dlsbqu3n4I65ujli/3rQ8Zk1MjmTOsz9+kTqOM4upsnQ6IWq/zeZTItMCgHpQhuhr4ip73honuzoJgge1cqWBFYvpabAPTOERTOP1kmx5SXPARX5uxyJzAiNILBC8zh7fGfNXOWV37O9gPNcivn6S9fB2Uhzqxb280Sz1OqOlLYK4Zd6grclXRmzd7jwWSX9V/ksh8wlbKD1hqmFU2Ekb/vTs/YZwJiVxHg==\", \"BAIDUID\": \"2A22611B8CFDAD87CAEFEF58E88BB9D4:FG=1\", \"CPID_212\": \"65828275\", \"CPTK_212\": \"1804289749\", \"HMACCOUNT\": \"974CCE1745E6D0B0\", \"SIGNIN_UC\": \"70a2711cf1d3d9b1a82d2f87d633bd8a04925705466xgmDyJP4kFoj02UQhjnnF0daGoWVq%2Fb6PQJwjiZbfhPIyGSneWCsPitfBRxvmBeJYx27YhT71FLie2DZnLWr%2BKxizdDEAzGcYIL7vMiDOa%2FKvYuB0yOH65tLbNl1aGx1AoH9H5v1kgYpvzNP8skaEE6ofBJaG%2B0A5wADj2%2B5Ov7sccDI9XNxTmewX1qiti%2B8S%2FHD0ARA1gxgFD6QcnQPJgZaZbkcjf2e2JCGCxBteYZfvIweCmKHPCwJ%2FwAQrSwMJhOXZrm39gkN6eRBTSfbOA%3D%3D77116481728614703881703584852345\", \"bdindexid\": \"3cjsf1fst2u74euquj61jiblc0\", \"BDUSS_BFESS\": \"pHTjJJV3RhTWVpNy1vR0dBUXJHZEp2NDZwaWtxR0FSMjlxSGoweFNPV1E0QVJvSVFBQUFBJCQAAAAAAQAAAAEAAAB5rwGWSm9zZW5DeQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJBT3WeQU91ncH\", \"__cas__rn__\": \"492570546\", \"BAIDUID_BFESS\": \"2A22611B8CFDAD87CAEFEF58E88BB9D4:FG=1\", \"__cas__id__212\": \"65828275\", \"__cas__st__212\": \"c79e86251dceddca16e4db6d89302cc438ecea1e19c1f7135907c5077cd34233bb95e14cf3d4952b19c50d14\", \"Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc\": \"1742558078\", \"Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc\": \"1742558098\"}', '2025-03-21 11:55:00'),
(3, 'test', '{\"RT\": \"\\\"z=1&dm=baidu.com&si=00be8a3e-a6dc-4bc4-ac56-8a578caec39e&ss=m984iqca&sl=7&tt=5m6&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=it1\\\"\", \"XFI\": \"51950390-1443-11f0-991d-a9b7031a1cd4\", \"XFT\": \"NiZHuvXR51PfummuKkD2gaKCbT0fLJpra19Vo2wID5c=\", \"XFCS\": \"16501F1384BC43C9D24883E7011B6F0D08A97B7DBC6975EB8D44F0AF95F63F65\", \"BDUSS\": \"lktZ29hNVoxcUwtNVk3U3FFMnRsQVhMTGJDMjZnQndsUEVRUFZiNjQxd3BVQnhvSVFBQUFBJCQAAAAAAQAAAAEAAAAVucsnQW1kb27YvEN5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACnD9Gcpw~RnQ\", \"ab_sr\": \"1.0.1_ZjY5MzI0ODgxY2IzMjIyNzhmMjhhZTRhZTBjZjk2ZDdhN2EwZDlhMzY0ZTcyNTQwZjQxN2YzY2RiOGU5OTRjY2JkYTcyNzM0ZGM2Mjk0MzMxNjhkODIwNWNiZjdmMjVhZWY4Mjc0YzAyMDg3MGNhMGJmNjU0NmU3MDYyZDhhZmZhNDZmYmJlN2Q0ODRkYWE5ZTRmNGRlODU5ZDQxZGY2ZQ==\", \"ppfuid\": \"FOCoIC3q5fKa8fgJnwzbE67EJ49BGJeplOzf+4l4EOvDuu2RXBRv6R3A1AZMa49I27C0gDDLrJyxcIIeAeEhD8JYsoLTpBiaCXhLqvzbzmvy3SeAW17tKgNq/Xx+RgOdb8TWCFe62MVrDTY6lMf2GrfqL8c87KLF2qFER3obJGmxOaJD7Qr04D9rET96PX99GEimjy3MrXEpSuItnI4KD2P5vWa8VVdqKPLBckQ0WyrgwNSQKKIDdXA6eDfuiw2FJ3ZBF1sLBqLP1Lik2nWCKk4sXpnMWzrlcw817brPPlfGgLbz7OSojK1zRbqBESR5Pdk2R9IA3lxxOVzA+Iw1TWLSgWjlFVG9Xmh1+20oPSbrzvDjYtVPmZ+9/6evcXmhcO1Y58MgLozKnaQIaLfWRHYJbniad6MOTaDR3XV1dTLxUSUZS0ReZYJMPG6nCsxNJlhI2UyeJA6QroZFMelR7tnTNS/pLMWceus0e757/UMPmrThfasmhDJrMFcBfoSrAAv3LCf1Y7/fHL3PTSf9vid/u2VLX4h1nBtx8EF07eCMhWVv+2qjbPV7ZhXk3reaWRFEeso3s/Kc9n/UXtUfNU1sHiCdbrCW5yYsuSM9SPGDZsl7FhTAKw7qIu38vFZiq+DRc8Vbf7jOiN9xPe0lOdZHUhGHZ82rL5jTCsILwcRVCndrarbwmu7G154MpYiKmTXZkqV7Alo4QZzicdyMbWvwvmR2/m//YVTM8qeZWgDSHjDmtehgLWM45zARbPujeqU0T92Gmgs89l2htrSKIVfEFzbtyzdes2f7rMR3DsT9s7hrTTo9fvI0eb7EXkrl28iVHWejeTfeu67KQzKLYpdImdyxYIjA1uSy2hfTFv/d3cnXH4nh+maaicAPllDg7JjsxZAfQoVAycJHizlQ5d34k8SzMID0x3kxnXwHfxXvz6DS3RnKydYTBUIWPYKJAEFefnSer1pU55Mw3PEJuMbPGO6Per4Y9UBohIIx5FdrGRChHnhPuJeIKACPXiVuli9ItRLEkdb1mLxNHAk3uJy88YX/Rf/sKUjR12zxRTDxxJNDJS+Dlsbqu3n4I65ujli/3rQ8Zk1MjmTOsz9+kTqOM4upsnQ6IWq/zeZTItMCgHpQhuhr4ip73honuzoJgge1cqWBFYvpabAPTOERTOP1kmx5SXPARX5uxyJzAiNILBC8zh7fGfNXOWV37O9gPNcivn6S9fB2Uhzqxb280Sz1OqOlLYK4Zd6grclXRmzd7jwWSX9V/ksh8wlbKD1hqmFU2Ekb/vTs/YZwJiVxHg==\", \"BAIDUID\": \"06AC0A86BB6AC5BBF1585A466EB90B8E:FG=1\", \"CPID_212\": \"60952149\", \"CPTK_212\": \"429062671\", \"HMACCOUNT\": \"9A887F4D727A151D\", \"SIGNIN_UC\": \"70a2711cf1d3d9b1a82d2f87d633bd8a04941064422EeVrf3ucKR%2FQM4O5BAq7epZlKfVbHyHx9P4gYkQjd5ffyp2W6UmenWK6OoiLl9uvQuxXaHbgXcSvafSCp9mkb8IhmpnyT3xsr%2BkhD46Ioe7sf1PApsjnmMyMVs0%2FtGZA3YkU%2BFqOhHpWAbP7tF25vHOXjYBymY5ffswmOuMddX3zmxXDR%2Fx9gfIkC%2FrhqUMqIEUKRT5%2B5jRzED2%2Boaho6IuSAc7KDR1ngz30qJajANRIgTl25a5x0IOdEDyNUn3N5r6CDENRM7nyuM6ULAH4yyJPAEQMpHXvGCjSdvk1TfI%3D43263203639697630192796561499060\", \"bdindexid\": \"bjfs6h3lskrhoecsgqoe151cb2\", \"BDUSS_BFESS\": \"lktZ29hNVoxcUwtNVk3U3FFMnRsQVhMTGJDMjZnQndsUEVRUFZiNjQxd3BVQnhvSVFBQUFBJCQAAAAAAQAAAAEAAAAVucsnQW1kb27YvEN5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACnD9Gcpw~RnQ\", \"__cas__rn__\": \"494106442\", \"BAIDUID_BFESS\": \"06AC0A86BB6AC5BBF1585A466EB90B8E:FG=1\", \"__cas__id__212\": \"60952149\", \"__cas__st__212\": \"4520bd44cc8ed2a5d376b6241541eeadc0582e70a81f2f58aed9b391dbf99335ed34ad25cb17f01ca8786c68\", \"Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc\": \"1744093976\", \"Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc\": \"1744093996\"}', '2025-04-08 06:33:25');

-- --------------------------------------------------------

--
-- 表的结构 `crowd_age_data`
--

CREATE TABLE `crowd_age_data` (
  `id` int(11) NOT NULL,
  `typeId` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `tgi` float NOT NULL,
  `rate` float NOT NULL,
  `keyword` varchar(100) NOT NULL,
  `date` date NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `crowd_age_data`
--

INSERT INTO `crowd_age_data` (`id`, `typeId`, `name`, `tgi`, `rate`, `keyword`, `date`, `created_at`) VALUES
(1, 1, '0-19', 53.1, 4.87, '养老', '2025-05-11', '2025-05-11 02:13:10'),
(2, 2, '20-29', 159.61, 28.88, '养老', '2025-05-11', '2025-05-11 02:13:10'),
(3, 3, '30-39', 115.28, 36.86, '养老', '2025-05-11', '2025-05-11 02:13:10'),
(4, 4, '40-49', 79.89, 18.57, '养老', '2025-05-11', '2025-05-11 02:13:10'),
(5, 5, '50+', 61.91, 10.82, '养老', '2025-05-11', '2025-05-11 02:13:10');

-- --------------------------------------------------------

--
-- 表的结构 `crowd_gender_data`
--

CREATE TABLE `crowd_gender_data` (
  `id` int(11) NOT NULL,
  `typeId` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `tgi` float NOT NULL,
  `rate` float NOT NULL,
  `keyword` varchar(100) NOT NULL,
  `date` date NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `crowd_gender_data`
--

INSERT INTO `crowd_gender_data` (`id`, `typeId`, `name`, `tgi`, `rate`, `keyword`, `date`, `created_at`) VALUES
(1, 0, '女', 107.98, 51.35, '养老', '2025-05-11', '2025-05-11 02:13:10'),
(2, 1, '男', 92.76, 48.65, '养老', '2025-05-11', '2025-05-11 02:13:10');

-- --------------------------------------------------------

--
-- 表的结构 `crowd_interest_data`
--

CREATE TABLE `crowd_interest_data` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `value` int(11) NOT NULL,
  `tgi` int(11) NOT NULL,
  `rate` float NOT NULL,
  `category` varchar(50) NOT NULL,
  `keyword` varchar(100) NOT NULL,
  `data_date` date NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `crowd_interest_data`
--

INSERT INTO `crowd_interest_data` (`id`, `name`, `value`, `tgi`, `rate`, `category`, `keyword`, `data_date`, `created_at`) VALUES
(1, '科技资讯', 71, 127, 0, '资讯', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(2, '社会时政', 63, 165, 0, '资讯', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(3, '网络奇闻', 17, 64, 0, '资讯', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(4, '全日制学校', 75, 128, 0, '教育培训', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(5, '基础教育科目', 63, 119, 0, '教育培训', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(6, '考试培训', 49, 163, 0, '教育培训', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(7, '语言学习', 38, 123, 0, '教育培训', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(8, '高等教育专业', 21, 116, 0, '教育培训', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(9, '技能培训', 20, 125, 0, '教育培训', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(10, '艺术培训', 19, 74, 0, '教育培训', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(11, 'K12课程培训', 11, 63, 0, '教育培训', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(12, '留学', 6, 140, 0, '教育培训', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(13, '体育培训', 2, 175, 0, '教育培训', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(14, '电影', 73, 102, 0, '影视音乐', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(15, '音乐', 65, 108, 0, '影视音乐', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(16, '电视剧', 59, 97, 0, '影视音乐', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(17, '动漫', 48, 90, 0, '影视音乐', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(18, '综艺', 42, 96, 0, '影视音乐', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(19, '影音APP', 35, 100, 0, '影视音乐', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(20, '直播', 34, 131, 0, '影视音乐', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(21, '戏曲曲艺', 17, 67, 0, '影视音乐', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(22, '广播电台', 1, 185, 0, '影视音乐', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(23, '纪录片', 0, 119, 0, '影视音乐', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(24, '保险', 56, 199, 0, '金融财经', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(25, '银行', 51, 172, 0, '金融财经', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(26, '股票', 38, 178, 0, '金融财经', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(27, '贷款', 27, 171, 0, '金融财经', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(28, '基金', 17, 469, 0, '金融财经', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(29, '贵金属', 15, 134, 0, '金融财经', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(30, '外汇', 14, 160, 0, '金融财经', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(31, '银行业务', 13, 174, 0, '金融财经', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(32, '债券', 11, 231, 0, '金融财经', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(33, '信托', 8, 770, 0, '金融财经', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(34, '疾病', 82, 110, 0, '医疗健康', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(35, '养生保健', 61, 104, 0, '医疗健康', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(36, '就医偏好', 58, 118, 0, '医疗健康', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(37, '药品', 58, 110, 0, '医疗健康', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(38, '医疗机构', 54, 156, 0, '医疗健康', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(39, '医疗服务', 38, 128, 0, '医疗健康', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(40, '整容整形', 23, 94, 0, '医疗健康', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(41, '医疗器械', 8, 167, 0, '医疗健康', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(42, '网络小说', 61, 114, 0, '书籍阅读', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(43, '文学', 43, 104, 0, '书籍阅读', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(44, '人文社科', 37, 287, 0, '书籍阅读', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(45, '经济管理', 21, 538, 0, '书籍阅读', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(46, '科技', 14, 271, 0, '书籍阅读', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(47, '报刊杂志', 11, 264, 0, '书籍阅读', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(48, '关注书籍', 11, 99, 0, '书籍阅读', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(49, '励志成功', 7, 222, 0, '书籍阅读', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(50, '少儿', 7, 71, 0, '书籍阅读', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(51, '艺术与摄影', 4, 85, 0, '书籍阅读', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(52, '国内游', 70, 126, 0, '旅游出行', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(53, '关注景点', 61, 130, 0, '旅游出行', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(54, '景点类型', 55, 134, 0, '旅游出行', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(55, '远途出行方式', 55, 134, 0, '旅游出行', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(56, '酒店', 37, 142, 0, '旅游出行', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(57, '出国游', 19, 146, 0, '旅游出行', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(58, '交通票务', 16, 172, 0, '旅游出行', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(59, '旅游网站偏好', 14, 166, 0, '旅游出行', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(60, '旅游主题', 8, 134, 0, '旅游出行', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(61, '本地周边游', 7, 212, 0, '旅游出行', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(62, '菜品', 66, 113, 0, '餐饮美食', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(63, '水果蔬菜', 55, 104, 0, '餐饮美食', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(64, '口味', 51, 105, 0, '餐饮美食', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(65, '烹饪和菜谱', 48, 96, 0, '餐饮美食', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(66, '休闲小食', 46, 116, 0, '餐饮美食', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(67, '品牌偏好', 26, 139, 0, '餐饮美食', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(68, '酒水', 24, 92, 0, '餐饮美食', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(69, '喝茶', 16, 101, 0, '餐饮美食', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(70, '菜系', 14, 113, 0, '餐饮美食', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(71, '餐馆档次', 9, 213, 0, '餐饮美食', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(72, '手机', 61, 128, 0, '家电数码', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(73, '电脑', 42, 169, 0, '家电数码', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(74, '大家电', 27, 106, 0, '家电数码', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(75, '家电关注品牌', 20, 143, 0, '家电数码', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(76, '办公数码设备', 12, 182, 0, '家电数码', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(77, '影音设备', 9, 114, 0, '家电数码', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(78, '摄影器材', 8, 137, 0, '家电数码', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(79, '智能设备', 6, 222, 0, '家电数码', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(80, '厨房电器', 5, 75, 0, '家电数码', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(81, '网络设备', 5, 133, 0, '家电数码', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(82, '社交通讯', 37, 229, 0, '软件应用', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(83, '系统工具', 30, 193, 0, '软件应用', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(84, '生活实用', 9, 157, 0, '软件应用', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(85, '手机美化', 9, 444, 0, '软件应用', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(86, '办公学习', 2, 93, 0, '软件应用', '养老', '2025-05-11', '2025-05-11 02:13:12'),
(87, '影音图像', 0, 264, 0, '软件应用', '养老', '2025-05-11', '2025-05-11 02:13:12');

-- --------------------------------------------------------

--
-- 表的结构 `crowd_region_data`
--

CREATE TABLE `crowd_region_data` (
  `id` int(11) NOT NULL,
  `province` varchar(50) NOT NULL,
  `value` int(11) NOT NULL,
  `keyword` varchar(100) NOT NULL,
  `date` date NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `crowd_region_data`
--

INSERT INTO `crowd_region_data` (`id`, `province`, `value`, `keyword`, `date`, `created_at`) VALUES
(1, '上海', 318, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(2, '云南', 201, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(3, '内蒙古', 106, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(4, '北京', 955, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(5, '台湾', 0, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(6, '吉林', 139, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(7, '四川', 430, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(8, '天津', 128, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(9, '宁夏', 27, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(10, '安徽', 268, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(11, '山东', 575, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(12, '山西', 307, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(13, '广东', 810, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(14, '广西', 256, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(15, '新疆', 122, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(16, '江苏', 513, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(17, '江西', 206, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(18, '河北', 603, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(19, '河南', 569, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(20, '浙江', 474, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(21, '海南', 50, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(22, '湖北', 374, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(23, '湖南', 195, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(24, '澳门', 5, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(25, '甘肃', 156, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(26, '福建', 206, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(27, '西藏', 0, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(28, '贵州', 139, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(29, '辽宁', 268, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(30, '重庆', 178, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(31, '陕西', 1000, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(32, '青海', 33, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(33, '香港', 5, '养老', '2025-05-10', '2025-05-11 02:13:09'),
(34, '黑龙江', 195, '养老', '2025-05-10', '2025-05-11 02:13:09');

-- --------------------------------------------------------

--
-- 表的结构 `human_request_data`
--

CREATE TABLE `human_request_data` (
  `id` int(11) NOT NULL,
  `word` varchar(255) NOT NULL,
  `pv` int(11) DEFAULT NULL,
  `ratio` decimal(10,2) DEFAULT NULL,
  `sim` decimal(10,2) DEFAULT NULL,
  `keyword` varchar(255) NOT NULL,
  `date` date NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- 表的结构 `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `password` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `email` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `role` varchar(20) COLLATE utf8_unicode_ci NOT NULL DEFAULT 'user',
  `last_login` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- 转存表中的数据 `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `phone`, `email`, `role`, `last_login`, `created_at`) VALUES
(1, 'admin', 'admin123', '13800138000', 'admin@example.com', 'admin', '2025-05-11 02:13:00', '2025-04-26 12:06:23'),
(2, 'test', 'Wen123321', '18584855132', '1402353365@qq.com', 'user', '2025-04-26 15:10:26', '2025-04-26 12:07:29'),
(3, 'test1', '123456', '18584855431', 'aa@qq.com', 'user', '2025-04-26 13:11:13', '2025-04-26 12:32:23');

--
-- 转储表的索引
--

--
-- 表的索引 `area_codes`
--
ALTER TABLE `area_codes`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_area` (`region`,`province`,`city`);

--
-- 表的索引 `baidu_index_trends`
--
ALTER TABLE `baidu_index_trends`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_trend` (`date`,`area`,`keyword`);

--
-- 表的索引 `cookies`
--
ALTER TABLE `cookies`
  ADD PRIMARY KEY (`id`),
  ADD KEY `username` (`username`);

--
-- 表的索引 `crowd_age_data`
--
ALTER TABLE `crowd_age_data`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_age` (`name`,`keyword`,`date`);

--
-- 表的索引 `crowd_gender_data`
--
ALTER TABLE `crowd_gender_data`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_gender` (`name`,`keyword`,`date`);

--
-- 表的索引 `crowd_interest_data`
--
ALTER TABLE `crowd_interest_data`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_interest` (`name`,`keyword`,`data_date`);

--
-- 表的索引 `crowd_region_data`
--
ALTER TABLE `crowd_region_data`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_region` (`province`,`keyword`,`date`);

--
-- 表的索引 `human_request_data`
--
ALTER TABLE `human_request_data`
  ADD PRIMARY KEY (`id`);

--
-- 表的索引 `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `phone` (`phone`),
  ADD UNIQUE KEY `email` (`email`);

--
-- 在导出的表使用AUTO_INCREMENT
--

--
-- 使用表AUTO_INCREMENT `area_codes`
--
ALTER TABLE `area_codes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=422;

--
-- 使用表AUTO_INCREMENT `baidu_index_trends`
--
ALTER TABLE `baidu_index_trends`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用表AUTO_INCREMENT `cookies`
--
ALTER TABLE `cookies`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- 使用表AUTO_INCREMENT `crowd_age_data`
--
ALTER TABLE `crowd_age_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- 使用表AUTO_INCREMENT `crowd_gender_data`
--
ALTER TABLE `crowd_gender_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- 使用表AUTO_INCREMENT `crowd_interest_data`
--
ALTER TABLE `crowd_interest_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=88;

--
-- 使用表AUTO_INCREMENT `crowd_region_data`
--
ALTER TABLE `crowd_region_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=35;

--
-- 使用表AUTO_INCREMENT `human_request_data`
--
ALTER TABLE `human_request_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用表AUTO_INCREMENT `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
