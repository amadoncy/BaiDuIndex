-- phpMyAdmin SQL Dump
-- version 4.8.5
-- https://www.phpmyadmin.net/
--
-- 主机： localhost
-- 生成日期： 2025-04-01 14:35:01
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
  `region` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `province` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `city` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `code` int(11) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- 转存表中的数据 `area_codes`
--

INSERT INTO `area_codes` (`id`, `region`, `province`, `city`, `code`, `created_at`) VALUES
(1, '华北', '北京', NULL, 911, '2025-03-22 05:39:52'),
(2, '华北', '北京', '东城区', 1001, '2025-03-22 05:39:52'),
(3, '华北', '北京', '西城区', 1002, '2025-03-22 05:39:52'),
(4, '华北', '北京', '朝阳区', 1003, '2025-03-22 05:39:52'),
(5, '华北', '北京', '海淀区', 1004, '2025-03-22 05:39:52'),
(6, '华北', '北京', '丰台区', 1005, '2025-03-22 05:39:52'),
(7, '华北', '北京', '石景山区', 1006, '2025-03-22 05:39:52'),
(8, '华北', '北京', '通州区', 1007, '2025-03-22 05:39:52'),
(9, '华北', '北京', '昌平区', 1008, '2025-03-22 05:39:52'),
(10, '华北', '天津', NULL, 923, '2025-03-22 05:39:52'),
(11, '华北', '天津', '和平区', 2001, '2025-03-22 05:39:52'),
(12, '华北', '天津', '河东区', 2002, '2025-03-22 05:39:52'),
(13, '华北', '天津', '河西区', 2003, '2025-03-22 05:39:52'),
(14, '华北', '天津', '南开区', 2004, '2025-03-22 05:39:52'),
(15, '华北', '天津', '河北区', 2005, '2025-03-22 05:39:52'),
(16, '华北', '天津', '红桥区', 2006, '2025-03-22 05:39:52'),
(17, '华北', '天津', '滨海新区', 2007, '2025-03-22 05:39:52'),
(18, '华北', '河北', NULL, 920, '2025-03-22 05:39:52'),
(19, '华北', '河北', '石家庄', 141, '2025-03-22 05:39:52'),
(20, '华北', '河北', '唐山', 261, '2025-03-22 05:39:52'),
(21, '华北', '河北', '秦皇岛', 148, '2025-03-22 05:39:52'),
(22, '华北', '河北', '邯郸', 292, '2025-03-22 05:39:52'),
(23, '华北', '河北', '邢台', 293, '2025-03-22 05:39:52'),
(24, '华北', '河北', '保定', 307, '2025-03-22 05:39:52'),
(25, '华北', '河北', '张家口', 264, '2025-03-22 05:39:52'),
(26, '华北', '河北', '承德', 207, '2025-03-22 05:39:52'),
(27, '华北', '河北', '沧州', 149, '2025-03-22 05:39:52'),
(28, '华北', '河北', '廊坊', 191, '2025-03-22 05:39:52'),
(29, '华北', '河北', '衡水', 208, '2025-03-22 05:39:52'),
(30, '华北', '山西', NULL, 915, '2025-03-22 05:39:52'),
(31, '华北', '山西', '太原', 176, '2025-03-22 05:39:52'),
(32, '华北', '山西', '大同', 355, '2025-03-22 05:39:52'),
(33, '华北', '山西', '阳泉', 357, '2025-03-22 05:39:52'),
(34, '华北', '山西', '长治', 356, '2025-03-22 05:39:52'),
(35, '华北', '山西', '晋城', 354, '2025-03-22 05:39:52'),
(36, '华北', '山西', '朔州', 359, '2025-03-22 05:39:52'),
(37, '华北', '山西', '晋中', 358, '2025-03-22 05:39:52'),
(38, '华北', '山西', '运城', 360, '2025-03-22 05:39:52'),
(39, '华北', '山西', '忻州', 361, '2025-03-22 05:39:52'),
(40, '华北', '山西', '临汾', 362, '2025-03-22 05:39:52'),
(41, '华北', '山西', '吕梁', 363, '2025-03-22 05:39:52'),
(42, '华北', '内蒙古', NULL, 918, '2025-03-22 05:39:52'),
(43, '华北', '内蒙古', '呼和浩特', 321, '2025-03-22 05:39:52'),
(44, '华北', '内蒙古', '包头', 229, '2025-03-22 05:39:52'),
(45, '华北', '内蒙古', '乌海', 123, '2025-03-22 05:39:52'),
(46, '华北', '内蒙古', '赤峰', 297, '2025-03-22 05:39:52'),
(47, '华北', '内蒙古', '通辽', 64, '2025-03-22 05:39:52'),
(48, '华北', '内蒙古', '鄂尔多斯', 283, '2025-03-22 05:39:52'),
(49, '华北', '内蒙古', '呼伦贝尔', 61, '2025-03-22 05:39:52'),
(50, '华北', '内蒙古', '巴彦淖尔', 169, '2025-03-22 05:39:52'),
(51, '华北', '内蒙古', '乌兰察布', 168, '2025-03-22 05:39:52'),
(52, '华北', '内蒙古', '兴安盟', 62, '2025-03-22 05:39:52'),
(53, '华北', '内蒙古', '锡林郭勒', 63, '2025-03-22 05:39:52'),
(54, '华北', '内蒙古', '阿拉善', 230, '2025-03-22 05:39:52'),
(55, '华东', '上海', NULL, 910, '2025-03-22 05:39:52'),
(56, '华东', '上海', '黄浦区', 3001, '2025-03-22 05:39:52'),
(57, '华东', '上海', '徐汇区', 3002, '2025-03-22 05:39:52'),
(58, '华东', '上海', '长宁区', 3003, '2025-03-22 05:39:52'),
(59, '华东', '上海', '静安区', 3004, '2025-03-22 05:39:52'),
(60, '华东', '上海', '普陀区', 3005, '2025-03-22 05:39:52'),
(61, '华东', '上海', '虹口区', 3006, '2025-03-22 05:39:52'),
(62, '华东', '上海', '杨浦区', 3007, '2025-03-22 05:39:52'),
(63, '华东', '上海', '浦东新区', 3008, '2025-03-22 05:39:52'),
(64, '华东', '江苏', NULL, 916, '2025-03-22 05:39:52'),
(65, '华东', '江苏', '南京', 125, '2025-03-22 05:39:52'),
(66, '华东', '江苏', '无锡', 127, '2025-03-22 05:39:52'),
(67, '华东', '江苏', '徐州', 316, '2025-03-22 05:39:52'),
(68, '华东', '江苏', '常州', 348, '2025-03-22 05:39:52'),
(69, '华东', '江苏', '苏州', 126, '2025-03-22 05:39:52'),
(70, '华东', '江苏', '南通', 161, '2025-03-22 05:39:52'),
(71, '华东', '江苏', '连云港', 347, '2025-03-22 05:39:52'),
(72, '华东', '江苏', '淮安', 162, '2025-03-22 05:39:52'),
(73, '华东', '江苏', '盐城', 223, '2025-03-22 05:39:52'),
(74, '华东', '江苏', '扬州', 346, '2025-03-22 05:39:52'),
(75, '华东', '江苏', '镇江', 160, '2025-03-22 05:39:52'),
(76, '华东', '江苏', '泰州', 224, '2025-03-22 05:39:52'),
(77, '华东', '江苏', '宿迁', 277, '2025-03-22 05:39:52'),
(78, '华东', '浙江', NULL, 917, '2025-03-22 05:39:52'),
(79, '华东', '浙江', '杭州', 138, '2025-03-22 05:39:52'),
(80, '华东', '浙江', '宁波', 289, '2025-03-22 05:39:52'),
(81, '华东', '浙江', '温州', 149, '2025-03-22 05:39:52'),
(82, '华东', '浙江', '嘉兴', 334, '2025-03-22 05:39:52'),
(83, '华东', '浙江', '湖州', 336, '2025-03-22 05:39:52'),
(84, '华东', '浙江', '绍兴', 333, '2025-03-22 05:39:52'),
(85, '华东', '浙江', '金华', 287, '2025-03-22 05:39:52'),
(86, '华东', '浙江', '衢州', 243, '2025-03-22 05:39:52'),
(87, '华东', '浙江', '舟山', 245, '2025-03-22 05:39:52'),
(88, '华东', '浙江', '台州', 244, '2025-03-22 05:39:52'),
(89, '华东', '浙江', '丽水', 292, '2025-03-22 05:39:52'),
(90, '华东', '安徽', NULL, 928, '2025-03-22 05:39:52'),
(91, '华东', '安徽', '合肥', 123, '2025-03-22 05:39:52'),
(92, '华东', '安徽', '芜湖', 181, '2025-03-22 05:39:52'),
(93, '华东', '安徽', '蚌埠', 182, '2025-03-22 05:39:52'),
(94, '华东', '安徽', '淮南', 254, '2025-03-22 05:39:52'),
(95, '华东', '安徽', '马鞍山', 183, '2025-03-22 05:39:52'),
(96, '华东', '安徽', '淮北', 253, '2025-03-22 05:39:52'),
(97, '华东', '安徽', '铜陵', 337, '2025-03-22 05:39:52'),
(98, '华东', '安徽', '安庆', 180, '2025-03-22 05:39:52'),
(99, '华东', '安徽', '黄山', 252, '2025-03-22 05:39:52'),
(100, '华东', '安徽', '滁州', 189, '2025-03-22 05:39:52'),
(101, '华东', '安徽', '阜阳', 128, '2025-03-22 05:39:52'),
(102, '华东', '安徽', '宿州', 370, '2025-03-22 05:39:52'),
(103, '华东', '安徽', '六安', 298, '2025-03-22 05:39:52'),
(104, '华东', '安徽', '亳州', 188, '2025-03-22 05:39:52'),
(105, '华东', '安徽', '池州', 299, '2025-03-22 05:39:52'),
(106, '华东', '安徽', '宣城', 190, '2025-03-22 05:39:52'),
(107, '华东', '福建', NULL, 909, '2025-03-22 05:39:52'),
(108, '华东', '福建', '福州', 134, '2025-03-22 05:39:52'),
(109, '华东', '福建', '厦门', 194, '2025-03-22 05:39:52'),
(110, '华东', '福建', '莆田', 195, '2025-03-22 05:39:52'),
(111, '华东', '福建', '三明', 254, '2025-03-22 05:39:52'),
(112, '华东', '福建', '泉州', 134, '2025-03-22 05:39:52'),
(113, '华东', '福建', '漳州', 255, '2025-03-22 05:39:52'),
(114, '华东', '福建', '南平', 253, '2025-03-22 05:39:52'),
(115, '华东', '福建', '龙岩', 193, '2025-03-22 05:39:52'),
(116, '华东', '福建', '宁德', 192, '2025-03-22 05:39:52'),
(117, '华东', '江西', NULL, 903, '2025-03-22 05:39:52'),
(118, '华东', '江西', '南昌', 163, '2025-03-22 05:39:52'),
(119, '华东', '江西', '景德镇', 225, '2025-03-22 05:39:52'),
(120, '华东', '江西', '萍乡', 350, '2025-03-22 05:39:52'),
(121, '华东', '江西', '九江', 349, '2025-03-22 05:39:52'),
(122, '华东', '江西', '新余', 164, '2025-03-22 05:39:52'),
(123, '华东', '江西', '鹰潭', 279, '2025-03-22 05:39:52'),
(124, '华东', '江西', '赣州', 365, '2025-03-22 05:39:52'),
(125, '华东', '江西', '吉安', 318, '2025-03-22 05:39:52'),
(126, '华东', '江西', '宜春', 278, '2025-03-22 05:39:52'),
(127, '华东', '江西', '抚州', 226, '2025-03-22 05:39:52'),
(128, '华东', '江西', '上饶', 364, '2025-03-22 05:39:52'),
(129, '华东', '山东', NULL, 901, '2025-03-22 05:39:52'),
(130, '华东', '山东', '济南', 288, '2025-03-22 05:39:52'),
(131, '华东', '山东', '青岛', 236, '2025-03-22 05:39:52'),
(132, '华东', '山东', '淄博', 354, '2025-03-22 05:39:52'),
(133, '华东', '山东', '枣庄', 172, '2025-03-22 05:39:52'),
(134, '华东', '山东', '东营', 174, '2025-03-22 05:39:52'),
(135, '华东', '山东', '烟台', 326, '2025-03-22 05:39:52'),
(136, '华东', '山东', '潍坊', 287, '2025-03-22 05:39:52'),
(137, '华东', '山东', '济宁', 286, '2025-03-22 05:39:52'),
(138, '华东', '山东', '泰安', 325, '2025-03-22 05:39:52'),
(139, '华东', '山东', '威海', 175, '2025-03-22 05:39:52'),
(140, '华东', '山东', '日照', 173, '2025-03-22 05:39:52'),
(141, '华东', '山东', '临沂', 234, '2025-03-22 05:39:52'),
(142, '华东', '山东', '德州', 372, '2025-03-22 05:39:52'),
(143, '华东', '山东', '聊城', 366, '2025-03-22 05:39:52'),
(144, '华东', '山东', '滨州', 235, '2025-03-22 05:39:52'),
(145, '华东', '山东', '菏泽', 353, '2025-03-22 05:39:52'),
(146, '华南', '广东', NULL, 913, '2025-03-22 05:39:52'),
(147, '华南', '广东', '广州', 95, '2025-03-22 05:39:52'),
(148, '华南', '广东', '深圳', 94, '2025-03-22 05:39:52'),
(149, '华南', '广东', '珠海', 140, '2025-03-22 05:39:52'),
(150, '华南', '广东', '汕头', 303, '2025-03-22 05:39:52'),
(151, '华南', '广东', '佛山', 138, '2025-03-22 05:39:52'),
(152, '华南', '广东', '韶关', 137, '2025-03-22 05:39:52'),
(153, '华南', '广东', '湛江', 198, '2025-03-22 05:39:52'),
(154, '华南', '广东', '肇庆', 338, '2025-03-22 05:39:52'),
(155, '华南', '广东', '江门', 302, '2025-03-22 05:39:52'),
(156, '华南', '广东', '茂名', 139, '2025-03-22 05:39:52'),
(157, '华南', '广东', '惠州', 301, '2025-03-22 05:39:52'),
(158, '华南', '广东', '梅州', 141, '2025-03-22 05:39:52'),
(159, '华南', '广东', '汕尾', 339, '2025-03-22 05:39:52'),
(160, '华南', '广东', '河源', 340, '2025-03-22 05:39:52'),
(161, '华南', '广东', '阳江', 199, '2025-03-22 05:39:52'),
(162, '华南', '广东', '清远', 197, '2025-03-22 05:39:52'),
(163, '华南', '广东', '东莞', 133, '2025-03-22 05:39:52'),
(164, '华南', '广东', '中山', 187, '2025-03-22 05:39:52'),
(165, '华南', '广东', '潮州', 201, '2025-03-22 05:39:52'),
(166, '华南', '广东', '揭阳', 200, '2025-03-22 05:39:52'),
(167, '华南', '广东', '云浮', 258, '2025-03-22 05:39:52'),
(168, '华南', '广西', NULL, 912, '2025-03-22 05:39:52'),
(169, '华南', '广西', '南宁', 261, '2025-03-22 05:39:52'),
(170, '华南', '广西', '柳州', 305, '2025-03-22 05:39:52'),
(171, '华南', '广西', '桂林', 142, '2025-03-22 05:39:52'),
(172, '华南', '广西', '梧州', 304, '2025-03-22 05:39:52'),
(173, '华南', '广西', '北海', 295, '2025-03-22 05:39:52'),
(174, '华南', '广西', '防城港', 204, '2025-03-22 05:39:52'),
(175, '华南', '广西', '钦州', 145, '2025-03-22 05:39:52'),
(176, '华南', '广西', '贵港', 144, '2025-03-22 05:39:52'),
(177, '华南', '广西', '玉林', 361, '2025-03-22 05:39:52'),
(178, '华南', '广西', '百色', 203, '2025-03-22 05:39:52'),
(179, '华南', '广西', '贺州', 260, '2025-03-22 05:39:52'),
(180, '华南', '广西', '河池', 143, '2025-03-22 05:39:52'),
(181, '华南', '广西', '来宾', 202, '2025-03-22 05:39:52'),
(182, '华南', '广西', '崇左', 205, '2025-03-22 05:39:52'),
(183, '华南', '海南', NULL, 906, '2025-03-22 05:39:52'),
(184, '华南', '海南', '海口', 125, '2025-03-22 05:39:52'),
(185, '华南', '海南', '三亚', 121, '2025-03-22 05:39:52'),
(186, '华南', '海南', '三沙', 122, '2025-03-22 05:39:52'),
(187, '华南', '海南', '儋州', 123, '2025-03-22 05:39:52'),
(188, '华南', '海南', '五指山', 129, '2025-03-22 05:39:52'),
(189, '华南', '海南', '琼海', 128, '2025-03-22 05:39:52'),
(190, '华南', '海南', '文昌', 127, '2025-03-22 05:39:52'),
(191, '华南', '海南', '万宁', 126, '2025-03-22 05:39:52'),
(192, '华南', '海南', '东方', 124, '2025-03-22 05:39:52'),
(193, '西南', '重庆', NULL, 904, '2025-03-22 05:39:52'),
(194, '西南', '重庆', '渝中区', 4001, '2025-03-22 05:39:52'),
(195, '西南', '重庆', '江北区', 4002, '2025-03-22 05:39:52'),
(196, '西南', '重庆', '南岸区', 4003, '2025-03-22 05:39:52'),
(197, '西南', '重庆', '沙坪坝区', 4004, '2025-03-22 05:39:52'),
(198, '西南', '重庆', '九龙坡区', 4005, '2025-03-22 05:39:52'),
(199, '西南', '重庆', '大渡口区', 4006, '2025-03-22 05:39:52'),
(200, '西南', '四川', NULL, 914, '2025-03-22 05:39:52'),
(201, '西南', '四川', '成都', 97, '2025-03-22 05:39:52'),
(202, '西南', '四川', '绵阳', 98, '2025-03-22 05:39:52'),
(203, '西南', '四川', '自贡', 111, '2025-03-22 05:39:52'),
(204, '西南', '四川', '攀枝花', 112, '2025-03-22 05:39:52'),
(205, '西南', '四川', '泸州', 103, '2025-03-22 05:39:52'),
(206, '西南', '四川', '德阳', 106, '2025-03-22 05:39:52'),
(207, '西南', '四川', '广元', 99, '2025-03-22 05:39:52'),
(208, '西南', '四川', '遂宁', 100, '2025-03-22 05:39:52'),
(209, '西南', '四川', '内江', 102, '2025-03-22 05:39:52'),
(210, '西南', '四川', '乐山', 107, '2025-03-22 05:39:52'),
(211, '西南', '四川', '南充', 104, '2025-03-22 05:39:52'),
(212, '西南', '四川', '宜宾', 96, '2025-03-22 05:39:52'),
(213, '西南', '四川', '广安', 108, '2025-03-22 05:39:52'),
(214, '西南', '四川', '达州', 113, '2025-03-22 05:39:52'),
(215, '西南', '四川', '眉山', 291, '2025-03-22 05:39:52'),
(216, '西南', '四川', '雅安', 114, '2025-03-22 05:39:52'),
(217, '西南', '四川', '巴中', 101, '2025-03-22 05:39:52'),
(218, '西南', '四川', '资阳', 109, '2025-03-22 05:39:52'),
(219, '西南', '四川', '阿坝', 457, '2025-03-22 05:39:52'),
(220, '西南', '四川', '甘孜', 417, '2025-03-22 05:39:52'),
(221, '西南', '四川', '凉山', 479, '2025-03-22 05:39:52'),
(222, '西南', '贵州', NULL, 929, '2025-03-22 05:39:52'),
(223, '西南', '贵州', '贵阳', 146, '2025-03-22 05:39:52'),
(224, '西南', '贵州', '六盘水', 147, '2025-03-22 05:39:52'),
(225, '西南', '贵州', '遵义', 262, '2025-03-22 05:39:52'),
(226, '西南', '贵州', '安顺', 263, '2025-03-22 05:39:52'),
(227, '西南', '贵州', '毕节', 148, '2025-03-22 05:39:52'),
(228, '西南', '贵州', '铜仁', 350, '2025-03-22 05:39:52'),
(229, '西南', '贵州', '黔西南', 351, '2025-03-22 05:39:52'),
(230, '西南', '贵州', '黔东南', 352, '2025-03-22 05:39:52'),
(231, '西南', '贵州', '黔南', 353, '2025-03-22 05:39:52'),
(232, '西南', '云南', NULL, 930, '2025-03-22 05:39:52'),
(233, '西南', '云南', '昆明', 117, '2025-03-22 05:39:52'),
(234, '西南', '云南', '曲靖', 249, '2025-03-22 05:39:52'),
(235, '西南', '云南', '玉溪', 250, '2025-03-22 05:39:52'),
(236, '西南', '云南', '保山', 251, '2025-03-22 05:39:52'),
(237, '西南', '云南', '昭通', 252, '2025-03-22 05:39:52'),
(238, '西南', '云南', '丽江', 253, '2025-03-22 05:39:52'),
(239, '西南', '云南', '普洱', 254, '2025-03-22 05:39:52'),
(240, '西南', '云南', '临沧', 255, '2025-03-22 05:39:52'),
(241, '西南', '云南', '楚雄', 256, '2025-03-22 05:39:52'),
(242, '西南', '云南', '红河', 257, '2025-03-22 05:39:52'),
(243, '西南', '云南', '文山', 258, '2025-03-22 05:39:52'),
(244, '西南', '云南', '西双版纳', 259, '2025-03-22 05:39:52'),
(245, '西南', '云南', '大理', 260, '2025-03-22 05:39:52'),
(246, '西南', '云南', '德宏', 261, '2025-03-22 05:39:52'),
(247, '西南', '云南', '怒江', 262, '2025-03-22 05:39:52'),
(248, '西南', '云南', '迪庆', 263, '2025-03-22 05:39:52'),
(249, '西南', '西藏', NULL, 934, '2025-03-22 05:39:52'),
(250, '西南', '西藏', '拉萨', 100, '2025-03-22 05:39:52'),
(251, '西南', '西藏', '日喀则', 101, '2025-03-22 05:39:52'),
(252, '西南', '西藏', '昌都', 102, '2025-03-22 05:39:52'),
(253, '西南', '西藏', '林芝', 103, '2025-03-22 05:39:52'),
(254, '西南', '西藏', '山南', 104, '2025-03-22 05:39:52'),
(255, '西南', '西藏', '那曲', 105, '2025-03-22 05:39:52'),
(256, '西南', '西藏', '阿里', 106, '2025-03-22 05:39:52'),
(257, '东北', '辽宁', NULL, 922, '2025-03-22 05:39:52'),
(258, '东北', '辽宁', '沈阳', 150, '2025-03-22 05:39:52'),
(259, '东北', '辽宁', '大连', 167, '2025-03-22 05:39:52'),
(260, '东北', '辽宁', '鞍山', 320, '2025-03-22 05:39:52'),
(261, '东北', '辽宁', '抚顺', 184, '2025-03-22 05:39:52'),
(262, '东北', '辽宁', '本溪', 227, '2025-03-22 05:39:52'),
(263, '东北', '辽宁', '丹东', 282, '2025-03-22 05:39:52'),
(264, '东北', '辽宁', '锦州', 166, '2025-03-22 05:39:52'),
(265, '东北', '辽宁', '营口', 281, '2025-03-22 05:39:52'),
(266, '东北', '辽宁', '阜新', 280, '2025-03-22 05:39:52'),
(267, '东北', '辽宁', '辽阳', 351, '2025-03-22 05:39:52'),
(268, '东北', '辽宁', '盘锦', 228, '2025-03-22 05:39:52'),
(269, '东北', '辽宁', '铁岭', 229, '2025-03-22 05:39:52'),
(270, '东北', '辽宁', '朝阳', 230, '2025-03-22 05:39:52'),
(271, '东北', '辽宁', '葫芦岛', 231, '2025-03-22 05:39:52'),
(272, '东北', '吉林', NULL, 921, '2025-03-22 05:39:52'),
(273, '东北', '吉林', '长春', 154, '2025-03-22 05:39:52'),
(274, '东北', '吉林', '吉林市', 183, '2025-03-22 05:39:52'),
(275, '东北', '吉林', '四平', 437, '2025-03-22 05:39:52'),
(276, '东北', '吉林', '辽源', 438, '2025-03-22 05:39:52'),
(277, '东北', '吉林', '通化', 439, '2025-03-22 05:39:52'),
(278, '东北', '吉林', '白山', 440, '2025-03-22 05:39:52'),
(279, '东北', '吉林', '松原', 441, '2025-03-22 05:39:52'),
(280, '东北', '吉林', '白城', 442, '2025-03-22 05:39:52'),
(281, '东北', '吉林', '延边', 443, '2025-03-22 05:39:52'),
(282, '东北', '黑龙江', NULL, 919, '2025-03-22 05:39:52'),
(283, '东北', '黑龙江', '哈尔滨', 152, '2025-03-22 05:39:52'),
(284, '东北', '黑龙江', '齐齐哈尔', 319, '2025-03-22 05:39:52'),
(285, '东北', '黑龙江', '鸡西', 459, '2025-03-22 05:39:52'),
(286, '东北', '黑龙江', '鹤岗', 460, '2025-03-22 05:39:52'),
(287, '东北', '黑龙江', '双鸭山', 461, '2025-03-22 05:39:52'),
(288, '东北', '黑龙江', '大庆', 153, '2025-03-22 05:39:52'),
(289, '东北', '黑龙江', '伊春', 462, '2025-03-22 05:39:52'),
(290, '东北', '黑龙江', '佳木斯', 454, '2025-03-22 05:39:52'),
(291, '东北', '黑龙江', '七台河', 463, '2025-03-22 05:39:52'),
(292, '东北', '黑龙江', '牡丹江', 318, '2025-03-22 05:39:52'),
(293, '东北', '黑龙江', '黑河', 464, '2025-03-22 05:39:52'),
(294, '东北', '黑龙江', '绥化', 455, '2025-03-22 05:39:52'),
(295, '东北', '黑龙江', '大兴安岭', 465, '2025-03-22 05:39:52'),
(296, '华中', '河南', NULL, 925, '2025-03-22 05:39:52'),
(297, '华中', '河南', '郑州', 168, '2025-03-22 05:39:52'),
(298, '华中', '河南', '开封', 210, '2025-03-22 05:39:52'),
(299, '华中', '河南', '洛阳', 169, '2025-03-22 05:39:52'),
(300, '华中', '河南', '平顶山', 213, '2025-03-22 05:39:52'),
(301, '华中', '河南', '安阳', 267, '2025-03-22 05:39:52'),
(302, '华中', '河南', '鹤壁', 215, '2025-03-22 05:39:52'),
(303, '华中', '河南', '新乡', 173, '2025-03-22 05:39:52'),
(304, '华中', '河南', '焦作', 174, '2025-03-22 05:39:52'),
(305, '华中', '河南', '濮阳', 176, '2025-03-22 05:39:52'),
(306, '华中', '河南', '许昌', 175, '2025-03-22 05:39:52'),
(307, '华中', '河南', '漯河', 216, '2025-03-22 05:39:52'),
(308, '华中', '河南', '三门峡', 212, '2025-03-22 05:39:52'),
(309, '华中', '河南', '南阳', 309, '2025-03-22 05:39:52'),
(310, '华中', '河南', '商丘', 177, '2025-03-22 05:39:52'),
(311, '华中', '河南', '信阳', 214, '2025-03-22 05:39:52'),
(312, '华中', '河南', '周口', 308, '2025-03-22 05:39:52'),
(313, '华中', '河南', '驻马店', 269, '2025-03-22 05:39:52'),
(314, '华中', '河南', '济源', 211, '2025-03-22 05:39:52'),
(315, '华中', '湖北', NULL, 928, '2025-03-22 05:39:52'),
(316, '华中', '湖北', '武汉', 218, '2025-03-22 05:39:52'),
(317, '华中', '湖北', '黄石', 311, '2025-03-22 05:39:52'),
(318, '华中', '湖北', '十堰', 216, '2025-03-22 05:39:52'),
(319, '华中', '湖北', '宜昌', 270, '2025-03-22 05:39:52'),
(320, '华中', '湖北', '襄阳', 217, '2025-03-22 05:39:52'),
(321, '华中', '湖北', '鄂州', 122, '2025-03-22 05:39:52'),
(322, '华中', '湖北', '荆门', 217, '2025-03-22 05:39:52'),
(323, '华中', '湖北', '孝感', 310, '2025-03-22 05:39:52'),
(324, '华中', '湖北', '荆州', 157, '2025-03-22 05:39:52'),
(325, '华中', '湖北', '黄冈', 271, '2025-03-22 05:39:52'),
(326, '华中', '湖北', '咸宁', 274, '2025-03-22 05:39:52'),
(327, '华中', '湖北', '随州', 273, '2025-03-22 05:39:52'),
(328, '华中', '湖北', '恩施', 373, '2025-03-22 05:39:52'),
(329, '华中', '湖南', NULL, 927, '2025-03-22 05:39:52'),
(330, '华中', '湖南', '长沙', 158, '2025-03-22 05:39:52'),
(331, '华中', '湖南', '株洲', 222, '2025-03-22 05:39:52'),
(332, '华中', '湖南', '湘潭', 313, '2025-03-22 05:39:52'),
(333, '华中', '湖南', '衡阳', 159, '2025-03-22 05:39:52'),
(334, '华中', '湖南', '邵阳', 273, '2025-03-22 05:39:52'),
(335, '华中', '湖南', '岳阳', 220, '2025-03-22 05:39:52'),
(336, '华中', '湖南', '常德', 219, '2025-03-22 05:39:52'),
(337, '华中', '湖南', '张家界', 312, '2025-03-22 05:39:52'),
(338, '华中', '湖南', '益阳', 272, '2025-03-22 05:39:52'),
(339, '华中', '湖南', '郴州', 275, '2025-03-22 05:39:52'),
(340, '华中', '湖南', '永州', 314, '2025-03-22 05:39:52'),
(341, '华中', '湖南', '怀化', 363, '2025-03-22 05:39:52'),
(342, '华中', '湖南', '娄底', 221, '2025-03-22 05:39:52'),
(343, '华中', '湖南', '湘西', 274, '2025-03-22 05:39:52'),
(344, '西北', '陕西', NULL, 924, '2025-03-22 05:39:52'),
(345, '西北', '陕西', '西安', 233, '2025-03-22 05:39:52'),
(346, '西北', '陕西', '铜川', 232, '2025-03-22 05:39:52'),
(347, '西北', '陕西', '宝鸡', 171, '2025-03-22 05:39:52'),
(348, '西北', '陕西', '咸阳', 323, '2025-03-22 05:39:52'),
(349, '西北', '陕西', '渭南', 170, '2025-03-22 05:39:52'),
(350, '西北', '陕西', '延安', 284, '2025-03-22 05:39:52'),
(351, '西北', '陕西', '汉中', 352, '2025-03-22 05:39:52'),
(352, '西北', '陕西', '榆林', 231, '2025-03-22 05:39:52'),
(353, '西北', '陕西', '安康', 324, '2025-03-22 05:39:52'),
(354, '西北', '陕西', '商洛', 285, '2025-03-22 05:39:53'),
(355, '西北', '甘肃', NULL, 931, '2025-03-22 05:39:53'),
(356, '西北', '甘肃', '兰州', 166, '2025-03-22 05:39:53'),
(357, '西北', '甘肃', '嘉峪关', 224, '2025-03-22 05:39:53'),
(358, '西北', '甘肃', '金昌', 225, '2025-03-22 05:39:53'),
(359, '西北', '甘肃', '白银', 226, '2025-03-22 05:39:53'),
(360, '西北', '甘肃', '天水', 169, '2025-03-22 05:39:53'),
(361, '西北', '甘肃', '武威', 283, '2025-03-22 05:39:53'),
(362, '西北', '甘肃', '张掖', 285, '2025-03-22 05:39:53'),
(363, '西北', '甘肃', '平凉', 286, '2025-03-22 05:39:53'),
(364, '西北', '甘肃', '酒泉', 284, '2025-03-22 05:39:53'),
(365, '西北', '甘肃', '庆阳', 281, '2025-03-22 05:39:53'),
(366, '西北', '甘肃', '定西', 282, '2025-03-22 05:39:53'),
(367, '西北', '甘肃', '陇南', 344, '2025-03-22 05:39:53'),
(368, '西北', '甘肃', '临夏', 346, '2025-03-22 05:39:53'),
(369, '西北', '甘肃', '甘南', 343, '2025-03-22 05:39:53'),
(370, '西北', '青海', NULL, 932, '2025-03-22 05:39:53'),
(371, '西北', '青海', '西宁', 139, '2025-03-22 05:39:53'),
(372, '西北', '青海', '海东', 140, '2025-03-22 05:39:53'),
(373, '西北', '青海', '海北', 141, '2025-03-22 05:39:53'),
(374, '西北', '青海', '黄南', 142, '2025-03-22 05:39:53'),
(375, '西北', '青海', '海南', 143, '2025-03-22 05:39:53'),
(376, '西北', '青海', '果洛', 144, '2025-03-22 05:39:53'),
(377, '西北', '青海', '玉树', 145, '2025-03-22 05:39:53'),
(378, '西北', '青海', '海西', 146, '2025-03-22 05:39:53'),
(379, '西北', '宁夏', NULL, 933, '2025-03-22 05:39:53'),
(380, '西北', '宁夏', '银川', 360, '2025-03-22 05:39:53'),
(381, '西北', '宁夏', '石嘴山', 335, '2025-03-22 05:39:53'),
(382, '西北', '宁夏', '吴忠', 322, '2025-03-22 05:39:53'),
(383, '西北', '宁夏', '固原', 246, '2025-03-22 05:39:53'),
(384, '西北', '宁夏', '中卫', 181, '2025-03-22 05:39:53'),
(385, '西北', '新疆', NULL, 926, '2025-03-22 05:39:53'),
(386, '西北', '新疆', '乌鲁木齐', 92, '2025-03-22 05:39:53'),
(387, '西北', '新疆', '克拉玛依', 95, '2025-03-22 05:39:53'),
(388, '西北', '新疆', '吐鲁番', 89, '2025-03-22 05:39:53'),
(389, '西北', '新疆', '哈密', 91, '2025-03-22 05:39:53'),
(390, '西北', '新疆', '昌吉', 93, '2025-03-22 05:39:53'),
(391, '西北', '新疆', '博尔塔拉', 88, '2025-03-22 05:39:53'),
(392, '西北', '新疆', '巴音郭楞', 86, '2025-03-22 05:39:53'),
(393, '西北', '新疆', '阿克苏', 85, '2025-03-22 05:39:53'),
(394, '西北', '新疆', '克孜勒苏', 84, '2025-03-22 05:39:53'),
(395, '西北', '新疆', '喀什', 83, '2025-03-22 05:39:53'),
(396, '西北', '新疆', '和田', 82, '2025-03-22 05:39:53'),
(397, '西北', '新疆', '伊犁', 90, '2025-03-22 05:39:53'),
(398, '西北', '新疆', '塔城', 94, '2025-03-22 05:39:53'),
(399, '西北', '新疆', '阿勒泰', 87, '2025-03-22 05:39:53');

-- --------------------------------------------------------

--
-- 表的结构 `baidu_index_trends`
--

CREATE TABLE `baidu_index_trends` (
  `id` int(11) NOT NULL,
  `date` date NOT NULL,
  `index_value` int(11) NOT NULL,
  `area` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `keyword` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- 表的结构 `cookies`
--

CREATE TABLE `cookies` (
  `id` int(11) NOT NULL,
  `username` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `cookie_data` json NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- 转存表中的数据 `cookies`
--

INSERT INTO `cookies` (`id`, `username`, `cookie_data`, `created_at`) VALUES
(1, '18584855132', '{\"RT\": \"\\\"z=1&dm=baidu.com&si=fdfc8173-778d-4c01-b1fa-b9de73d5e640&ss=m8y3ny78&sl=5&tt=2ow&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf\\\"\", \"XFI\": \"215c4450-0ec0-11f0-907b-9fcb34bd1561\", \"XFT\": \"jbRhX368xBY1wVFKaRjcZukrLkTvKlhSwcARi+kSLaQ=\", \"XFCS\": \"357F46D13CCEC7756C21534EAD5B5D224EF4C8224C74C5EBA22546DD5A9C9619\", \"BDUSS\": \"nl5VEJiTHBrZ2VabzhORUctR1Eya0RtejZES2FaQkpkTU9iM0NsOURPaXFFQk5vSVFBQUFBJCQAAAAAAQAAAAEAAAAVucsnQW1kb27YvEN5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKqD62eqg-tnd\", \"ab_sr\": \"1.0.1_NWM0Yzk2NjE4OTI1NzliNTk0NDg4MTA1OWQwNmYzMmY3Y2E5ZjI0YzBhMWJkMzRjNWUxZjM4MWEwYzEzNDk0YjgzYjcyNjMwOGU5NmJjOWUwZjQzMTA2NGRjMGQzYmM2MTIyNDI2ZjEzN2NkNzJkNzFjOTliNzVhYzRiNGJkNzZkYjcyODI4YzRiMmU2YjFkZjdhMzRmZTMxMDgzMmJiOA==\", \"ppfuid\": \"FOCoIC3q5fKa8fgJnwzbE67EJ49BGJeplOzf+4l4EOvDuu2RXBRv6R3A1AZMa49I27C0gDDLrJyxcIIeAeEhD8JYsoLTpBiaCXhLqvzbzmvy3SeAW17tKgNq/Xx+RgOdb8TWCFe62MVrDTY6lMf2GrfqL8c87KLF2qFER3obJGmxOaJD7Qr04D9rET96PX99GEimjy3MrXEpSuItnI4KD2P5vWa8VVdqKPLBckQ0WyrgwNSQKKIDdXA6eDfuiw2FJ3ZBF1sLBqLP1Lik2nWCKk4sXpnMWzrlcw817brPPlfGgLbz7OSojK1zRbqBESR5Pdk2R9IA3lxxOVzA+Iw1TWLSgWjlFVG9Xmh1+20oPSbrzvDjYtVPmZ+9/6evcXmhcO1Y58MgLozKnaQIaLfWRHYJbniad6MOTaDR3XV1dTLxUSUZS0ReZYJMPG6nCsxNJlhI2UyeJA6QroZFMelR7tnTNS/pLMWceus0e757/UMPmrThfasmhDJrMFcBfoSrAAv3LCf1Y7/fHL3PTSf9vid/u2VLX4h1nBtx8EF07eCMhWVv+2qjbPV7ZhXk3reaWRFEeso3s/Kc9n/UXtUfNU1sHiCdbrCW5yYsuSM9SPGDZsl7FhTAKw7qIu38vFZiq+DRc8Vbf7jOiN9xPe0lOdZHUhGHZ82rL5jTCsILwcRVCndrarbwmu7G154MpYiKmTXZkqV7Alo4QZzicdyMbWvwvmR2/m//YVTM8qeZWgDSHjDmtehgLWM45zARbPujeqU0T92Gmgs89l2htrSKIVfEFzbtyzdes2f7rMR3DsT9s7hrTTo9fvI0eb7EXkrl28iVHWejeTfeu67KQzKLYpdImdyxYIjA1uSy2hfTFv/d3cnXH4nh+maaicAPllDg7JjsxZAfQoVAycJHizlQ5d34k8SzMID0x3kxnXwHfxXvz6DS3RnKydYTBUIWPYKJAEFefnSer1pU55Mw3PEJuMbPGO6Per4Y9UBohIIx5FdrGRChHnhPuJeIKACPXiVuli9ItRLEkdb1mLxNHAk3uJy88YX/Rf/sKUjR12zxRTDxxJNDJS+Dlsbqu3n4I65ujli/3rQ8Zk1MjmTOsz9+kTqOM4upsnQ6IWq/zeZTItMCgHpQhuhr4ip73honuzoJgge1cqWBFYvpabAPTOERTOP1kmx5SXPARX5uxyJzAiNILBC8zh7fGfNXOWV37O9gPNcivn6S9fB2Uhzqxb280Sz1OqOlLYK4Zd6grclXRmzd7jwWSX9V/ksh8wlbKD1hqmFU2Ekb/vTs/YZwJiVxHg==\", \"BAIDUID\": \"9E282DF7EC71EF4FB46431412666590F:FG=1\", \"CPID_212\": \"60952149\", \"CPTK_212\": \"935467119\", \"HMACCOUNT\": \"100369B37427ED22\", \"SIGNIN_UC\": \"70a2711cf1d3d9b1a82d2f87d633bd8a04935003644BqbVBAQew%2B5hpuKkTVcPlHnZx0Dseu5y%2FL%2FrP8ZLM5AlTI9JvC697nr9OotUnWe4b%2BLmYyGo6cgqzWsIo%2FhpBZCQefYl6o%2Fm6u1egdaW2C2UDsmBp15Pdvxpw3xHWaIeZu1P2QU2kLqH0IYFuA8Y%2F8KsWdXy5%2FKwRKq2ZsxFPYNPLan3SWJZZhjHxhUKfEnuxEYqj%2BHqp5Ab6oHQEDBpoWIm0iDyCohTWpxAOTF10QC%2B0mvEGZZNEuCjgdTDxcpaH0t48UYoC%2FlrDrypVW2AjqpBuaBCK3uU3fsPMTqMs%2F0%3D02149855355240415559301722990820\", \"__cas__rn__\": \"493500364\", \"BAIDUID_BFESS\": \"9E282DF7EC71EF4FB46431412666590F:FG=1\", \"__cas__id__212\": \"60952149\", \"__cas__st__212\": \"1d64fdf32775ce32acbcec29bb0b60dbaad56df0471b1e468a9f254e6b68f51e2e7f17d57b13e60a009f9d2e\", \"Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc\": \"1743487876\", \"Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc\": \"1743487918\"}', '2025-04-01 06:11:57'),
(2, '18781162981', '{\"RT\": \"\\\"z=1&dm=baidu.com&si=71fca3b2-b66d-40bb-b9df-d49c9f6c9ad9&ss=m8iq35ql&sl=2&tt=4oj&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=goq\\\"\", \"BDUSS\": \"pHTjJJV3RhTWVpNy1vR0dBUXJHZEp2NDZwaWtxR0FSMjlxSGoweFNPV1E0QVJvSVFBQUFBJCQAAAAAAQAAAAEAAAB5rwGWSm9zZW5DeQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJBT3WeQU91ncH\", \"ab_sr\": \"1.0.1_Yzc4NjFkOTQ4MTY5NTAzYTM5YmUzNDRlMTJkMTM4NTEzNmMzY2UwOWY1YWZkNmI5ZDM5ZDhkMjUxMjgyZmQ3OTUzZjIzYmJiZWUzMWFhMTBhMzUyY2UyZGYwYTc0NmJkZDM2MjllYzU3NmMxZWVjYmFkYzJlODQ3MDkxNTFiZjBmZmQ1NWFlYWUyNzJkMThjY2FmOWY1ZWE0ZGFiZDkxYw==\", \"ppfuid\": \"FOCoIC3q5fKa8fgJnwzbE67EJ49BGJeplOzf+4l4EOvDuu2RXBRv6R3A1AZMa49I27C0gDDLrJyxcIIeAeEhD8JYsoLTpBiaCXhLqvzbzmvy3SeAW17tKgNq/Xx+RgOdb8TWCFe62MVrDTY6lMf2GrfqL8c87KLF2qFER3obJGmxOaJD7Qr04D9rET96PX99GEimjy3MrXEpSuItnI4KD2P5vWa8VVdqKPLBckQ0WyrgwNSQKKIDdXA6eDfuiw2FJ3ZBF1sLBqLP1Lik2nWCKk4sXpnMWzrlcw817brPPlfGgLbz7OSojK1zRbqBESR5Pdk2R9IA3lxxOVzA+Iw1TWLSgWjlFVG9Xmh1+20oPSbrzvDjYtVPmZ+9/6evcXmhcO1Y58MgLozKnaQIaLfWRHYJbniad6MOTaDR3XV1dTLxUSUZS0ReZYJMPG6nCsxNJlhI2UyeJA6QroZFMelR7tnTNS/pLMWceus0e757/UMPmrThfasmhDJrMFcBfoSrAAv3LCf1Y7/fHL3PTSf9vid/u2VLX4h1nBtx8EF07eCMhWVv+2qjbPV7ZhXk3reaWRFEeso3s/Kc9n/UXtUfNU1sHiCdbrCW5yYsuSM9SPGDZsl7FhTAKw7qIu38vFZiq+DRc8Vbf7jOiN9xPe0lOdZHUhGHZ82rL5jTCsILwcRVCndrarbwmu7G154MpYiKmTXZkqV7Alo4QZzicdyMbWvwvmR2/m//YVTM8qeZWgDSHjDmtehgLWM45zARbPujeqU0T92Gmgs89l2htrSKIVfEFzbtyzdes2f7rMR3DsT9s7hrTTo9fvI0eb7EXkrl28iVHWejeTfeu67KQzKLYpdImdyxYIjA1uSy2hfTFv/d3cnXH4nh+maaicAPllDg7JjsxZAfQoVAycJHizlQ5d34k8SzMID0x3kxnXwHfxXvz6DS3RnKydYTBUIWPYKJAEFefnSer1pU55Mw3PEJuMbPGO6Per4Y9UBohIIx5FdrGRChHnhPuJeIKACPXiVuli9ItRLEkdb1mLxNHAk3uJy88YX/Rf/sKUjR12zxRTDxxJNDJS+Dlsbqu3n4I65ujli/3rQ8Zk1MjmTOsz9+kTqOM4upsnQ6IWq/zeZTItMCgHpQhuhr4ip73honuzoJgge1cqWBFYvpabAPTOERTOP1kmx5SXPARX5uxyJzAiNILBC8zh7fGfNXOWV37O9gPNcivn6S9fB2Uhzqxb280Sz1OqOlLYK4Zd6grclXRmzd7jwWSX9V/ksh8wlbKD1hqmFU2Ekb/vTs/YZwJiVxHg==\", \"BAIDUID\": \"2A22611B8CFDAD87CAEFEF58E88BB9D4:FG=1\", \"CPID_212\": \"65828275\", \"CPTK_212\": \"1804289749\", \"HMACCOUNT\": \"974CCE1745E6D0B0\", \"SIGNIN_UC\": \"70a2711cf1d3d9b1a82d2f87d633bd8a04925705466xgmDyJP4kFoj02UQhjnnF0daGoWVq%2Fb6PQJwjiZbfhPIyGSneWCsPitfBRxvmBeJYx27YhT71FLie2DZnLWr%2BKxizdDEAzGcYIL7vMiDOa%2FKvYuB0yOH65tLbNl1aGx1AoH9H5v1kgYpvzNP8skaEE6ofBJaG%2B0A5wADj2%2B5Ov7sccDI9XNxTmewX1qiti%2B8S%2FHD0ARA1gxgFD6QcnQPJgZaZbkcjf2e2JCGCxBteYZfvIweCmKHPCwJ%2FwAQrSwMJhOXZrm39gkN6eRBTSfbOA%3D%3D77116481728614703881703584852345\", \"bdindexid\": \"3cjsf1fst2u74euquj61jiblc0\", \"BDUSS_BFESS\": \"pHTjJJV3RhTWVpNy1vR0dBUXJHZEp2NDZwaWtxR0FSMjlxSGoweFNPV1E0QVJvSVFBQUFBJCQAAAAAAQAAAAEAAAB5rwGWSm9zZW5DeQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJBT3WeQU91ncH\", \"__cas__rn__\": \"492570546\", \"BAIDUID_BFESS\": \"2A22611B8CFDAD87CAEFEF58E88BB9D4:FG=1\", \"__cas__id__212\": \"65828275\", \"__cas__st__212\": \"c79e86251dceddca16e4db6d89302cc438ecea1e19c1f7135907c5077cd34233bb95e14cf3d4952b19c50d14\", \"Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc\": \"1742558078\", \"Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc\": \"1742558098\"}', '2025-03-21 11:55:00'),
(3, 'test', '{\"RT\": \"\\\"z=1&dm=baidu.com&si=fdfc8173-778d-4c01-b1fa-b9de73d5e640&ss=m8y3ny78&sl=5&tt=2ow&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf\\\"\", \"XFI\": \"215c4450-0ec0-11f0-907b-9fcb34bd1561\", \"XFT\": \"jbRhX368xBY1wVFKaRjcZukrLkTvKlhSwcARi+kSLaQ=\", \"XFCS\": \"357F46D13CCEC7756C21534EAD5B5D224EF4C8224C74C5EBA22546DD5A9C9619\", \"BDUSS\": \"nl5VEJiTHBrZ2VabzhORUctR1Eya0RtejZES2FaQkpkTU9iM0NsOURPaXFFQk5vSVFBQUFBJCQAAAAAAQAAAAEAAAAVucsnQW1kb27YvEN5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKqD62eqg-tnd\", \"ab_sr\": \"1.0.1_NWM0Yzk2NjE4OTI1NzliNTk0NDg4MTA1OWQwNmYzMmY3Y2E5ZjI0YzBhMWJkMzRjNWUxZjM4MWEwYzEzNDk0YjgzYjcyNjMwOGU5NmJjOWUwZjQzMTA2NGRjMGQzYmM2MTIyNDI2ZjEzN2NkNzJkNzFjOTliNzVhYzRiNGJkNzZkYjcyODI4YzRiMmU2YjFkZjdhMzRmZTMxMDgzMmJiOA==\", \"ppfuid\": \"FOCoIC3q5fKa8fgJnwzbE67EJ49BGJeplOzf+4l4EOvDuu2RXBRv6R3A1AZMa49I27C0gDDLrJyxcIIeAeEhD8JYsoLTpBiaCXhLqvzbzmvy3SeAW17tKgNq/Xx+RgOdb8TWCFe62MVrDTY6lMf2GrfqL8c87KLF2qFER3obJGmxOaJD7Qr04D9rET96PX99GEimjy3MrXEpSuItnI4KD2P5vWa8VVdqKPLBckQ0WyrgwNSQKKIDdXA6eDfuiw2FJ3ZBF1sLBqLP1Lik2nWCKk4sXpnMWzrlcw817brPPlfGgLbz7OSojK1zRbqBESR5Pdk2R9IA3lxxOVzA+Iw1TWLSgWjlFVG9Xmh1+20oPSbrzvDjYtVPmZ+9/6evcXmhcO1Y58MgLozKnaQIaLfWRHYJbniad6MOTaDR3XV1dTLxUSUZS0ReZYJMPG6nCsxNJlhI2UyeJA6QroZFMelR7tnTNS/pLMWceus0e757/UMPmrThfasmhDJrMFcBfoSrAAv3LCf1Y7/fHL3PTSf9vid/u2VLX4h1nBtx8EF07eCMhWVv+2qjbPV7ZhXk3reaWRFEeso3s/Kc9n/UXtUfNU1sHiCdbrCW5yYsuSM9SPGDZsl7FhTAKw7qIu38vFZiq+DRc8Vbf7jOiN9xPe0lOdZHUhGHZ82rL5jTCsILwcRVCndrarbwmu7G154MpYiKmTXZkqV7Alo4QZzicdyMbWvwvmR2/m//YVTM8qeZWgDSHjDmtehgLWM45zARbPujeqU0T92Gmgs89l2htrSKIVfEFzbtyzdes2f7rMR3DsT9s7hrTTo9fvI0eb7EXkrl28iVHWejeTfeu67KQzKLYpdImdyxYIjA1uSy2hfTFv/d3cnXH4nh+maaicAPllDg7JjsxZAfQoVAycJHizlQ5d34k8SzMID0x3kxnXwHfxXvz6DS3RnKydYTBUIWPYKJAEFefnSer1pU55Mw3PEJuMbPGO6Per4Y9UBohIIx5FdrGRChHnhPuJeIKACPXiVuli9ItRLEkdb1mLxNHAk3uJy88YX/Rf/sKUjR12zxRTDxxJNDJS+Dlsbqu3n4I65ujli/3rQ8Zk1MjmTOsz9+kTqOM4upsnQ6IWq/zeZTItMCgHpQhuhr4ip73honuzoJgge1cqWBFYvpabAPTOERTOP1kmx5SXPARX5uxyJzAiNILBC8zh7fGfNXOWV37O9gPNcivn6S9fB2Uhzqxb280Sz1OqOlLYK4Zd6grclXRmzd7jwWSX9V/ksh8wlbKD1hqmFU2Ekb/vTs/YZwJiVxHg==\", \"BAIDUID\": \"9E282DF7EC71EF4FB46431412666590F:FG=1\", \"CPID_212\": \"60952149\", \"CPTK_212\": \"935467119\", \"HMACCOUNT\": \"100369B37427ED22\", \"SIGNIN_UC\": \"70a2711cf1d3d9b1a82d2f87d633bd8a04935003644BqbVBAQew%2B5hpuKkTVcPlHnZx0Dseu5y%2FL%2FrP8ZLM5AlTI9JvC697nr9OotUnWe4b%2BLmYyGo6cgqzWsIo%2FhpBZCQefYl6o%2Fm6u1egdaW2C2UDsmBp15Pdvxpw3xHWaIeZu1P2QU2kLqH0IYFuA8Y%2F8KsWdXy5%2FKwRKq2ZsxFPYNPLan3SWJZZhjHxhUKfEnuxEYqj%2BHqp5Ab6oHQEDBpoWIm0iDyCohTWpxAOTF10QC%2B0mvEGZZNEuCjgdTDxcpaH0t48UYoC%2FlrDrypVW2AjqpBuaBCK3uU3fsPMTqMs%2F0%3D02149855355240415559301722990820\", \"__cas__rn__\": \"493500364\", \"BAIDUID_BFESS\": \"9E282DF7EC71EF4FB46431412666590F:FG=1\", \"__cas__id__212\": \"60952149\", \"__cas__st__212\": \"1d64fdf32775ce32acbcec29bb0b60dbaad56df0471b1e468a9f254e6b68f51e2e7f17d57b13e60a009f9d2e\", \"Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc\": \"1743487876\", \"Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc\": \"1743487918\"}', '2025-04-01 06:12:03');

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
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `email` varchar(100) NOT NULL,
  `last_login` datetime DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `phone`, `email`, `last_login`, `created_at`, `updated_at`) VALUES
(1, 'admin', 'Wen123321', '18584855132', '1402353365@qq.com', '2025-03-21 14:43:02', '2025-03-03 11:14:55', '2025-03-21 06:43:02'),
(2, 'test', 'Wen123321..', '18584855333', '222@qq.com', '2025-04-01 14:34:18', '2025-03-21 15:26:52', '2025-04-01 06:34:18');

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=400;

--
-- 使用表AUTO_INCREMENT `baidu_index_trends`
--
ALTER TABLE `baidu_index_trends`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用表AUTO_INCREMENT `cookies`
--
ALTER TABLE `cookies`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- 使用表AUTO_INCREMENT `crowd_age_data`
--
ALTER TABLE `crowd_age_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用表AUTO_INCREMENT `crowd_gender_data`
--
ALTER TABLE `crowd_gender_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用表AUTO_INCREMENT `crowd_interest_data`
--
ALTER TABLE `crowd_interest_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用表AUTO_INCREMENT `crowd_region_data`
--
ALTER TABLE `crowd_region_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用表AUTO_INCREMENT `human_request_data`
--
ALTER TABLE `human_request_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用表AUTO_INCREMENT `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
