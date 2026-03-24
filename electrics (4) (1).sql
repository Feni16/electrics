-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 11, 2026 at 02:50 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `electrics`
--

-- --------------------------------------------------------

--
-- Table structure for table `ai_chat`
--

CREATE TABLE `ai_chat` (
  `id` int(11) NOT NULL,
  `user_message` text DEFAULT NULL,
  `ai_reply` text DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `ai_chat`
--

INSERT INTO `ai_chat` (`id`, `user_message`, `ai_reply`, `created_at`, `user_id`) VALUES
(1, 'fan not working ..', 'Fan not working? Please check power, regulator, or capacitor. I can book a technician if needed.', '2026-02-24 05:08:11', 38),
(2, 'hi', 'Hello 👋 How can I assist you with your electrical issue today?', '2026-02-25 04:53:01', 44),
(3, 'hi', 'Hello 👋 How can I assist you with your electrical issue today?', '2026-02-25 05:58:26', 44),
(4, 'my fan not working', 'Fan not working? Please check power supply, regulator, or capacitor. I can book a technician if needed.', '2026-02-25 05:58:34', 44),
(5, 'ac  not', 'Please describe your electrical issue clearly.', '2026-02-25 05:58:40', 44),
(6, 'hey', 'Hello! How can I help you today?', '2026-03-11 04:49:25', 44),
(7, 'fan is not working', 'Our support team is available 24/7! Technicians work from 9 AM to 9 PM.', '2026-03-11 04:49:32', 44),
(8, 'ac', 'For specific technical queries, please describe your problem in detail.', '2026-03-11 04:52:22', 44),
(9, 'ac not working', 'Our support team is available 24/7! Technicians work from 9 AM to 9 PM.', '2026-03-11 04:52:28', 44),
(10, 'ok technician number', 'We have 11 skilled technicians available to serve you. They are experienced and professional!', '2026-03-11 04:52:40', 44),
(11, 'like?', 'For specific technical queries, please describe your problem in detail.', '2026-03-11 04:52:50', 44);

-- --------------------------------------------------------

--
-- Table structure for table `booking`
--

CREATE TABLE `booking` (
  `id` int(11) NOT NULL,
  `description` varchar(500) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `technician_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `is_read` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `booking`
--

INSERT INTO `booking` (`id`, `description`, `status`, `customer_id`, `technician_id`, `user_id`, `created_at`, `is_read`) VALUES
(1, 'ngdutdfcidhojdpkwdvb', 'Pending', 44, 2, 0, '2026-02-25 13:50:43', 0),
(2, 'ffdbgdbtkl;;.,mjnbvc ', 'Completed', 44, 2, 0, '2026-02-25 13:50:43', 0);

-- --------------------------------------------------------

--
-- Table structure for table `contact_messages`
--

CREATE TABLE `contact_messages` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `message` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `contact_messages`
--

INSERT INTO `contact_messages` (`id`, `name`, `email`, `message`, `created_at`) VALUES
(1, 'FENI BHUVA', 'fenibhuva20@gnu.ac.in', 'abncdefghihbveugnvkdn n,a nilnkfn ', '2026-02-05 05:41:42'),
(2, 'sachi', 'sachi@gmail.com', 'hii bvfynvfhkbdu aciefa', '2026-02-05 05:42:18'),
(3, 'zeelyo', 'zeelprajapati@gmail.com', 'frgurunvned,', '2026-02-05 05:53:50'),
(4, 'FENI BHUVA', 'fenibhuva20@gnu.ac.in', 'b  ,bnknkjbh, ,m', '2026-02-05 08:17:50'),
(5, 'FENI BHUVA', 'fenibhuva20@gnu.ac.in', 'hiii im feniii', '2026-02-06 07:59:56');

-- --------------------------------------------------------

--
-- Table structure for table `emergency_requests`
--

CREATE TABLE `emergency_requests` (
  `id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `description` text NOT NULL,
  `status` enum('Pending','Assigned','Resolved') NOT NULL DEFAULT 'Pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `feedback`
--

CREATE TABLE `feedback` (
  `id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `service_request_id` int(11) DEFAULT NULL,
  `rating` tinyint(4) NOT NULL CHECK (`rating` between 1 and 5),
  `comment` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `likes` int(11) DEFAULT 0,
  `ai_reply` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `feedback`
--

INSERT INTO `feedback` (`id`, `customer_id`, `service_request_id`, `rating`, `comment`, `created_at`, `likes`, `ai_reply`) VALUES
(1, 38, NULL, 4, 'niceeee', '2026-02-24 02:28:08', 0, 'Thanks for sharing your experience!');

-- --------------------------------------------------------

--
-- Table structure for table `feedbacks`
--

CREATE TABLE `feedbacks` (
  `id` int(11) NOT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `comment` text DEFAULT NULL,
  `rating` int(11) DEFAULT NULL,
  `likes` int(11) DEFAULT NULL,
  `ai_reply` text DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `feedbacks`
--

INSERT INTO `feedbacks` (`id`, `customer_id`, `comment`, `rating`, `likes`, `ai_reply`, `created_at`) VALUES
(1, 44, 'DadC', 5, 0, 'Thanks for your feedback. We appreciate it!', '2026-03-09 08:48:43');

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `message` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `is_read` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notifications`
--

INSERT INTO `notifications` (`id`, `message`, `created_at`, `user_id`, `is_read`) VALUES
(1, 'New booking from zeeeeeeeee', '2026-02-25 13:29:59', 0, 0),
(2, 'New booking from zeeeeeeeee', '2026-02-26 10:15:18', 0, 0),
(3, 'New booking from zeeeeeeeee', '2026-02-26 10:25:13', 0, 0),
(4, 'New booking from zeeeeeeeee', '2026-02-26 10:29:45', 0, 0),
(5, 'New booking from zeeeeeeeee', '2026-02-26 10:43:43', 0, 0),
(6, 'New booking from zeeeeeeeee', '2026-02-26 10:54:02', 0, 0),
(7, '🆕 zeeeeeeeee booked Wiring Service (Emergency)', '2026-03-01 18:03:24', 2, 0),
(8, 'Your account status has been updated to pending', '2026-03-10 04:44:35', 1, 0),
(9, 'Your account status has been updated to completed', '2026-03-10 04:45:04', 44, 0),
(10, 'Your account status has been updated to pending', '2026-03-10 04:45:20', 13, 0),
(11, 'Your account status has been updated to In Progress', '2026-03-10 04:51:13', 6, 0),
(12, '🔔 New booking from zeeeeeeeee for MCB Replacement', '2026-03-11 04:58:56', 2, 0),
(13, '✅ Your booking for MCB Replacement has been created', '2026-03-11 04:58:56', 44, 0);

-- --------------------------------------------------------

--
-- Table structure for table `payments`
--

CREATE TABLE `payments` (
  `id` int(11) NOT NULL,
  `request_id` int(11) NOT NULL,
  `amount` float DEFAULT NULL,
  `method` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `paid_at` datetime DEFAULT NULL,
  `technician_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `service`
--

CREATE TABLE `service` (
  `id` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `price` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `service`
--

INSERT INTO `service` (`id`, `name`, `description`, `price`) VALUES
(1, 'AC Repair', 'Air conditioner servicing and repair', 500),
(2, 'MCB Replacement', 'Replace damaged MCB switch', 300),
(3, 'Wiring Service', 'Complete home wiring solution', 1500),
(4, 'Fan Installation', 'Ceiling fan fitting and setup', 400);

-- --------------------------------------------------------

--
-- Table structure for table `service_categories`
--

CREATE TABLE `service_categories` (
  `id` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `price` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `service_categories`
--

INSERT INTO `service_categories` (`id`, `name`, `description`, `price`) VALUES
(1, 'Home Wiring & Repair', 'Complete home wiring and repair service', 500),
(2, 'Fan Installation / Repair', 'Ceiling and wall fan service', 300),
(3, 'Light Installation', 'LED, tube light and panel installation', 200),
(4, 'Switch & Socket Repair', 'Repair or replace switches and sockets', 150),
(5, 'Short Circuit Repair', 'Fix short circuit and power issues', 600),
(6, 'Inverter Installation', 'Inverter setup and maintenance', 800),
(7, 'AC Wiring', 'AC electrical wiring and power setup', 700),
(8, 'Electrical Safety Inspection', 'Complete safety and load inspection', 400),
(9, 'Fan Repair', 'Ceiling fan and exhaust fan repair', 300),
(10, 'Light Repair', 'Bulb, tube light, wiring issues', 200),
(11, 'Switch Board Repair', 'Switch & socket repair', 250),
(12, 'AC Repair', 'Air conditioner service & repair', 1500),
(13, 'Wiring Work', 'House wiring and short circuit fix', 500);

-- --------------------------------------------------------

--
-- Table structure for table `service_requests`
--

CREATE TABLE `service_requests` (
  `id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `service_id` int(11) NOT NULL,
  `technician_id` int(11) DEFAULT NULL,
  `status` enum('pending','in_progress','completed') NOT NULL DEFAULT 'pending',
  `request_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `rating` int(11) DEFAULT NULL,
  `feedback` varchar(255) DEFAULT NULL,
  `feedback_given` tinyint(1) DEFAULT 0,
  `title` varchar(150) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `address` text DEFAULT NULL,
  `room` varchar(50) NOT NULL,
  `urgency` varchar(50) NOT NULL,
  `payment_amount` float DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT 0,
  `created_at` datetime DEFAULT current_timestamp(),
  `image_filename` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `service_requests`
--

INSERT INTO `service_requests` (`id`, `customer_id`, `service_id`, `technician_id`, `status`, `request_date`, `rating`, `feedback`, `feedback_given`, `title`, `description`, `address`, `room`, `urgency`, `payment_amount`, `is_read`, `created_at`, `image_filename`) VALUES
(2, 32, 1, NULL, 'completed', '2026-02-05 23:25:40', NULL, NULL, 0, 'fan not working ', 'my fan not working...', 'Kherva,Mehsana,Gujarat', '', '', NULL, 0, '2026-02-25 10:17:35', NULL),
(4, 44, 4, NULL, 'pending', '2026-02-24 04:04:52', NULL, NULL, 0, 'noriihscabcn;lzcms', 'masnkjhkjnc;lxAL;SKA:/', 'tb road ,mehsana , 2..', 'Bathroom', 'Emergency', 0, 0, '2026-02-25 10:17:35', NULL),
(5, 44, 1, 2, 'pending', '2026-02-24 23:35:41', NULL, NULL, 0, 'Manual Booking', 'wsdfghjnbvcxcvbn,jyt543wertyuiolkjnbvc', 'Not Provided', 'Not Provided', 'Normal', 299, 0, '2026-02-25 05:05:41', NULL),
(6, 44, 2, NULL, 'pending', '2026-02-25 01:03:44', NULL, NULL, 0, 'MCB Replacement', NULL, 'Not Provided', 'Not Provided', 'Normal', 300, 0, '2026-02-25 06:33:44', NULL),
(7, 44, 2, 2, 'pending', '2026-02-25 02:29:59', NULL, NULL, 0, 'MCB Replacement', NULL, 'Not Provided', 'Not Provided', 'Normal', 300, 0, '2026-02-25 07:59:59', NULL),
(8, 44, 3, 2, 'pending', '2026-02-25 23:15:18', NULL, NULL, 0, 'Wiring Service', NULL, 'Not Provided', 'Not Provided', 'Normal', 1500, 0, '2026-02-26 04:45:18', NULL),
(9, 44, 3, 2, 'pending', '2026-02-25 23:25:13', NULL, NULL, 0, 'Wiring Service', NULL, 'Not Provided', 'Not Provided', 'Normal', 1500, 0, '2026-02-26 04:55:13', NULL),
(10, 44, 2, 2, 'pending', '2026-02-25 23:29:45', NULL, NULL, 0, 'MCB Replacement', NULL, 'Not Provided', 'Not Provided', 'Normal', 300, 0, '2026-02-26 04:59:45', NULL),
(11, 44, 3, 2, 'pending', '2026-02-25 23:43:43', NULL, NULL, 0, 'Wiring Service', NULL, 'Not Provided', 'Not Provided', 'Normal', 1500, 0, '2026-02-26 05:13:43', NULL),
(12, 44, 2, 2, 'pending', '2026-02-25 23:54:02', NULL, NULL, 0, 'MCB Replacement', NULL, 'Not Provided', 'Not Provided', 'Normal', 300, 0, '2026-02-26 05:24:02', NULL),
(13, 44, 2, 2, 'pending', '2026-02-26 00:26:08', NULL, NULL, 0, 'MCB Replacement', NULL, 'Not Provided', 'Not Provided', 'Normal', 300, 0, '2026-02-26 05:56:08', NULL),
(14, 44, 2, 2, 'pending', '2026-02-26 00:43:47', NULL, NULL, 0, 'MCB Replacement', NULL, 'Not Provided', 'Not Provided', 'Normal', 300, 0, '2026-02-26 06:13:47', NULL),
(15, 44, 2, 2, 'pending', '2026-02-26 02:02:08', NULL, NULL, 0, 'MCB Replacement', NULL, 'Not Provided', 'Not Provided', 'Normal', 300, 0, '2026-02-26 07:32:08', NULL),
(16, 44, 2, 2, 'pending', '2026-02-26 02:15:50', NULL, NULL, 0, 'fcvgbhnjmk', 'fghjkl,', 'gygbsdnvmfdgmdflkm', 'Kitchen', 'Normal', 300, 0, '2026-02-26 07:45:50', NULL),
(17, 1, 1, 2, 'completed', '2026-02-27 14:42:06', NULL, NULL, 0, 'Fan Repair', 'Fan not working', 'Test Address', 'Living Room', 'Normal', 299, 0, '2026-02-27 20:12:06', NULL),
(18, 1, 2, 2, 'completed', '2026-02-27 14:42:06', NULL, NULL, 0, 'Switch Repair', 'Switch not working', 'Test Address', 'Bedroom', 'Urgent', 399, 0, '2026-02-27 20:12:06', NULL),
(19, 2, 3, 2, 'completed', '2026-02-27 14:42:06', NULL, NULL, 0, 'AC Service', 'AC not cooling', 'Test Address', 'Hall', 'Emergency', 1499, 0, '2026-02-27 20:12:06', NULL),
(20, 44, 3, 2, '', '2026-03-01 07:03:24', NULL, NULL, 0, 'Wiring Service', 'ac not working ..........', 'tb road ,mehsana , 2.. 384002 ', 'Bedroom', 'Emergency', 1500, 0, '2026-03-01 12:33:24', NULL),
(21, 44, 2, 2, 'pending', '2026-03-11 04:58:56', NULL, NULL, 0, 'sdfgbnm', 'dfvfbgbgbbbbbb', 'tb road ,mehsana , 2.. 384002', 'Office', 'Urgent', 300, 0, '2026-03-11 04:58:56', '1773205136_OIP.jpg');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('customer','admin','technician') NOT NULL DEFAULT 'customer',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `phone` varchar(20) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `profile_image` varchar(255) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'Active',
  `specialization` varchar(100) DEFAULT NULL,
  `salary` int(11) DEFAULT NULL,
  `rating` float DEFAULT NULL,
  `address` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `password`, `role`, `created_at`, `phone`, `location`, `profile_image`, `status`, `specialization`, `salary`, `rating`, `address`) VALUES
(1, 'dev', 'dv@electrics.com', 'scrypt:32768:8:1$mvwVMkdonPYX8es1$065bb92745099b26e4b51b643dda7b367345b922be10f72197067d0518d664e96b45f1c8e611866af6928fd1c14e5f0cc08f3fe2044ddb5eac558dcc8d3058fd', 'customer', '2026-01-28 07:55:30', NULL, NULL, NULL, 'Pending', NULL, NULL, NULL, NULL),
(2, 'sp', 'sp@electrics.com', 'scrypt:32768:8:1$C3gjLG6F0BEfjzZG$f8820f98f787ac635e88d1267263d93d75503d26aa58d1275a44483111f0daed22864bffab6504067b7e5677b6c8b6a5ac55126e154ef285fc9ce262e503f4d6', 'technician', '2026-01-28 08:27:52', '', '', NULL, 'Active', '', NULL, NULL, NULL),
(5, 'admin', 'admin@electrics.com', 'scrypt:32768:8:1$uRM5UaP1o8TnDBIY$6a0f5250283124cdbfae493199b7f545a0ed562b83c33f75c94c5cac2462563e01d42252f5122b75f5f03704ba30b1c85d0dc4fe6f16b162f1aca01625b71c04', 'admin', '2026-01-28 08:56:42', '4561237456', NULL, NULL, 'Active', NULL, NULL, NULL, NULL),
(6, 'sachi', 'sachi@gmail.com', 'scrypt:32768:8:1$C99oPyngko5I3Tqy$a4fdae24ea894965a8b73891083f4ae98d4392b8725769116fcec8a4c16b3404c367f647891db33aff29679c9e9986973c7bcb4816ecb357102535f28b6b4570', 'customer', '2026-02-03 09:00:05', '6352607999', NULL, NULL, 'In Progress', NULL, NULL, NULL, NULL),
(7, 'Feni', 'fenibhuva161@gmail.com', 'scrypt:32768:8:1$gxpElD0anmiauIyL$a292d3183a3fe43825f9d4867e3af00a366ed44512b282fb030cde8bacab934a38e3addf8262b2bd5548901a384e11f33e3804c0cde652a7d455b692e9c12869', 'technician', '2026-02-03 09:02:18', '6352607999', NULL, NULL, 'Active', NULL, NULL, NULL, NULL),
(9, 'zeel', 'zeelprajapati@gmail.com', 'scrypt:32768:8:1$0jBTZraVOIDrm3fn$f1c6b500c01a0e837b51ff33f80d96fa00ccaa40bf35d0e323657a202c59224959ef8efe909cf24bda8a9999603db3a0ad73e03cdb3f1efeb71db4041433017d', 'customer', '2026-02-04 05:01:50', '6352607999', NULL, NULL, 'Active', NULL, NULL, NULL, NULL),
(10, 'diya', 'diya@gmail.com', 'scrypt:32768:8:1$EJnRbeQobgjttJqs$a59ce94a368b7f711ef2c0a561f15a0751a02fc916a50615f19e9d9f9b3f7335f4e8d5342c87d2dc1a510b5d396c98cdaf93f946ad69edc7996de2d927678026', 'technician', '2026-02-05 04:43:26', '1234567890', NULL, NULL, 'Active', NULL, NULL, NULL, NULL),
(13, 'dhruma', 'dhruma@gmail.com', 'scrypt:32768:8:1$ZfRi4bw9kVrN76ov$b8d9764d912780452869eb067d6ef500a59b2a78d6ecc89ca6834fad09995b5f134bc1f851a61cd1c46b29c68452abafa1acfc07393ff613d2dbcd58e4184776', 'customer', '2026-02-05 04:57:10', '6352607999', NULL, NULL, 'Pending', NULL, NULL, NULL, NULL),
(17, 'riddhi', 'riddhi@gmail.com', 'scrypt:32768:8:1$qwouzRIDcVTQP0CM$ed9edf4916db182567a7e4699fc0ddefe399e0f35733f574fb6d8d6d7d4f16177ac7831d46d85e8d077cb2e8e62b05f47cda66908bce945ccbb72b45320a131b', 'technician', '2026-02-05 05:00:24', '7894561130', NULL, NULL, 'Active', NULL, NULL, NULL, NULL),
(18, 'Feni Bhuva', 'fenibhuva@gmail.com', 'scrypt:32768:8:1$iHIQaAfCp4zrGabt$717827371474853479976f06aa5ce0615d8438c39bc349b2aa7a5cb2cc391084f20329a1c5bb761e35a349fc29f1ce7d1394fb71e924334b578891444067bd82', 'customer', '2026-02-05 05:15:35', '6352607999', NULL, NULL, 'Active', NULL, NULL, NULL, NULL),
(21, 'jyoti', 'jyoti@gmail.com', 'scrypt:32768:8:1$QGy6H9EfnNRC1ruY$162acd8df169842f1572834a0eefceaf25cfd45f51feb98d2908b73ef890d9513b6e10639c32decb3e0bc00daf63c54d86b9a8466fd9e47107bbdd1eb217ef82', 'admin', '2026-02-05 07:57:04', '6352607999', NULL, NULL, 'Active', NULL, NULL, NULL, NULL),
(22, 'abc', 'abc@gmail.com', 'scrypt:32768:8:1$ocC8e0jOR3d2Qqt3$5762258e8a85cd772a7170a03b1b462e17f6de99ef74d609c1b4f90293316a128459ec438aa2c3b76ca3c1ce939b99c6bfd230b6db6ed1437b68b11cbf97abe7', 'customer', '2026-02-05 08:40:02', '6352607999', '', NULL, 'Active', NULL, NULL, NULL, NULL),
(26, 'swedrft', 'fenibhuva20@gnu.ac.in', 'scrypt:32768:8:1$ifsrXlO2ytYNxTQ1$47b89b91029a29d0517181de6a7acb2f536f58d580736a82aea1eb7e183439f290f958a3cdea45d0e93c15db238060643c78f6456a0eefad1b0bfa24b51d82ca', 'customer', '2026-02-05 09:44:31', '6352607999', '', NULL, 'Active', NULL, NULL, NULL, NULL),
(27, 'maitri', 'maitri12@gmail.com', 'scrypt:32768:8:1$Lptll0oh0OaIMnfF$a42b40fb9a6c6cee6694a057fbc5e1c9de1702fd3ab5c52ab3ee410e3030dc45035fd5a80562e8dbe2ca863ff70ffbe2b5cb526a63efb2dc0dae9c6f903f8f1a', 'technician', '2026-02-05 09:47:04', '6352607999', '', NULL, 'Active', NULL, NULL, NULL, NULL),
(28, 'pizza', 'pizza@gmail.com', 'scrypt:32768:8:1$NQAmoPzYtTMmrmGs$9198dedf5d73c266cc46a10c9b178c08d2fcd444c7933b4184697a0d4e1af8d10704eaa5cde46764ad589d69326c0330dfc86ea510ab59fabf343f97562dc7fd', 'admin', '2026-02-05 09:48:13', '6352607999', '', NULL, 'Active', NULL, NULL, NULL, NULL),
(29, 'burger', 'burger@gmail.com', 'scrypt:32768:8:1$k7NiXn4fcJQes8gq$ec72aa7c06f0f656b5fb728003452dc2a9fedd7d359e5c69368d064b501fcffe0083da9b87a37f4a745c25802aeac75a9514266a37b95433657fc98a7231bbfd', 'technician', '2026-02-05 09:55:02', '6352607999', '', NULL, 'Active', NULL, NULL, NULL, NULL),
(30, 'sandwich', 'sandwich@gmail.com', 'scrypt:32768:8:1$FVhGdEjekQipl2Fa$c2d7147304026133a7398ca1d9b45500ffd2afb979cc70e10200dc5b648fffe652275dd75640a0caa9544e88c2afb4fc46569baf0d7e9672583c48f2fb0aec30', 'customer', '2026-02-05 14:03:34', '6352607999', '', NULL, 'Active', NULL, NULL, NULL, NULL),
(31, 'puff', 'puff@gmail.com', 'scrypt:32768:8:1$j00ROXLgFH8RURRu$acf185e70dc30106ce9ae04e17f74e2d3e7194b3d648e2151cb635f94157490cbb13053ee7d09f7b621805f1a0ab5b27d607919ab0e3f6120d700a969185975a', 'technician', '2026-02-06 04:32:40', '6352607999', '', NULL, 'Active', NULL, NULL, NULL, NULL),
(32, 'pqr', 'pqr@gmail.com', 'scrypt:32768:8:1$6q9vYX1YcjYjmBA8$8328fbb064a1f682ef79cf8c622b74810d81d53bfff47955600afa1c26f25db1538bfa6db6777e5ddfaae77592eb4643762573261bb9eb477a526125d1e272d9', 'customer', '2026-02-06 04:35:31', '1234567890', '', NULL, 'Active', NULL, NULL, NULL, NULL),
(33, 'asdf', 'asdf@gmail.com', 'scrypt:32768:8:1$dAcxMmxlGf6Q12qk$9db5e658e71d9e2f2e32b93568539e233d1568ce626697fa81853de8b3f8b6ac7756d38bb2d3295b89cc5d8d1c026fb5e835a377ffe5534d5ae9ae625a4d1624', 'customer', '2026-02-06 05:15:57', '1234567890', '', NULL, 'Active', NULL, NULL, NULL, NULL),
(34, 'zeelu', 'zeel20@gmail.com', 'scrypt:32768:8:1$kKKUHxuzJpsi9eg9$7e64921d5f12ddae483024c045a19758f0b3ee080789f35f489e487e22e4ceb8ef43370bd1bd43198c360e0a839338d354e99b40ea49403cc8ccf02e0fdeb108', 'customer', '2026-02-06 05:32:22', '6352607999', '', NULL, 'Active', NULL, NULL, NULL, NULL),
(35, 'zeel20', 'zeel21@gmail.com', 'scrypt:32768:8:1$qKvmdg7P8gXg1708$42232a3e8fc5ed1ce902c134e2ddb2215fd6d9ea5a36c1e7fdb26218245b55ba4bc66046aa4b01e4e10ade1eb7071cf0e3e8d8c31e941d35df56544233fee955', 'customer', '2026-02-06 05:33:56', '1234567890', '', NULL, 'Active', NULL, NULL, NULL, NULL),
(36, 'pizza1', 'pizza1@gmail.com', 'scrypt:32768:8:1$eSLPOGEdhly2SO6Y$0b8e6a4ae2ac77ac148fb1c8048fa0139ef854d9c9b2587978dec3045178203c5fb67b11ae61623eaa646835e62a57db25da3a3b61baf531cd3e4fb3fe98c910', 'technician', '2026-02-06 07:52:52', '6352607999', '', NULL, 'Active', NULL, NULL, NULL, NULL),
(37, 'sachi1', 'sachi1@gmail.com', 'scrypt:32768:8:1$nspdfSAkbp8wDUB7$1bd8982e20eb8cc4f1f44209c62196289165431923c1cb578b255a622ef3483ad0e669d50218e9c8e772a28dc2d82957ee0341d98f6048c7f60ec8ae3ba96cc9', 'admin', '2026-02-06 07:57:39', '6352607999', '', NULL, 'Active', NULL, NULL, NULL, NULL),
(38, 'sachi17', 'sachipatel17@gmail.com', 'scrypt:32768:8:1$xpVnpkMluaqWxu9E$c9fb01d8413b5ca68edcb59d5efcda45860c4c231cdaefb03a9982cc9dd6a2484591f0d6f2f88b2597bf1c25fdbb1ac3f7dea6b2d5721d5129c57b098ddc771e', 'customer', '2026-02-23 23:20:47', '45612374564', '', NULL, 'Active', NULL, NULL, NULL, NULL),
(39, 'zxxc', 'zeelprajapati20@gnu.ac.in', 'scrypt:32768:8:1$EK5XKqPwYEt5T3s7$75b0f827fb7c2686b8adbcbf4cf99b618b75e659a8798f66b001e4a7aa06f016049c24e439def3d97e5f2ff823d7984056bd3b99f17e207d0d8ca73eec5aa389', 'technician', '2026-02-23 23:59:37', '5426813579', '', NULL, 'Active', NULL, NULL, NULL, NULL),
(40, 'admin1', 'admin1@electrics.com', 'scrypt:32768:8:1$E5l71NIQJ28EKPFR$7f480bf9cd3e7e7f65d6dd4365868239d00a9dc0d91ea984d50f49b1ab2b3475d844c322e65189f12e0aa0fed29379a2e2b14228b44e6a2cda7b1778089f33e0', 'admin', '2026-02-24 00:02:24', '45612374564', '', NULL, 'Active', NULL, NULL, NULL, NULL),
(41, 'zxcv', 'admin20@gnu.ac.in', 'scrypt:32768:8:1$tTIiv27TZxkFN8SW$2710a78fd9328b76ed5fe281cec0b4c47dd759e4fb9f2a5bfe85ca1ff3490562c397a6d21c4164d1daf763649a1c261165b1aef7fb25512fb4feeb2af02b4919', 'admin', '2026-02-24 00:03:35', '1234578124', '', NULL, 'Active', NULL, NULL, NULL, NULL),
(42, 'tech123', 'tech2@electrics.com', 'scrypt:32768:8:1$OUc6phhRu0oFh1yn$0ab0f2340ed39d17740e677e9ed711800fce902d980dc3bff248eca44cdb4ed0fdf7c201bef7fc84fadc25c2fc4872370deb9f33a669c986551c04ed92f5a7a9', 'technician', '2026-02-24 02:32:18', '1234578124', '', NULL, 'Active', NULL, NULL, NULL, NULL),
(43, 'garlic', 'garlic@gmail.com', 'scrypt:32768:8:1$hSlNqo1J47U0HlvB$2c038749faf76bac6751467473c3576a4c98a49a5b6dd5a4cfe1e2d86b24b9d66ee4366f74ece06ada0eff5c9ac5a69fca7423117a68eed9877dbe0c5a3def27', 'technician', '2026-02-24 02:53:27', '01234567890', '', NULL, 'Active', NULL, NULL, NULL, NULL),
(44, 'zeeeeeeeee', 'zeel@gmail.com', 'scrypt:32768:8:1$irsIFjN76L6CZ4zf$d09631844d88814d89583262b9aea1f94ac399e60c7e195b7631ae0b3d5ef0fa3d81fa4c4745d2ea9fb6541cee535888607f59bdcbd2c0158f5759d54d479b38', 'customer', '2026-02-24 04:04:22', '1234578124', 'mahesana', 'anarkaliwoman.jpg', 'Completed', NULL, NULL, NULL, NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `ai_chat`
--
ALTER TABLE `ai_chat`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `booking`
--
ALTER TABLE `booking`
  ADD PRIMARY KEY (`id`),
  ADD KEY `customer_id` (`customer_id`),
  ADD KEY `technician_id` (`technician_id`);

--
-- Indexes for table `contact_messages`
--
ALTER TABLE `contact_messages`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `emergency_requests`
--
ALTER TABLE `emergency_requests`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_emergency_customer` (`customer_id`);

--
-- Indexes for table `feedback`
--
ALTER TABLE `feedback`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_feedback_customer` (`customer_id`),
  ADD KEY `fk_feedback_request` (`service_request_id`);

--
-- Indexes for table `feedbacks`
--
ALTER TABLE `feedbacks`
  ADD PRIMARY KEY (`id`),
  ADD KEY `customer_id` (`customer_id`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `payments`
--
ALTER TABLE `payments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `request_id` (`request_id`);

--
-- Indexes for table `service`
--
ALTER TABLE `service`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `service_categories`
--
ALTER TABLE `service_categories`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `service_requests`
--
ALTER TABLE `service_requests`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_customer` (`customer_id`),
  ADD KEY `fk_service` (`service_id`),
  ADD KEY `fk_technician` (`technician_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `ai_chat`
--
ALTER TABLE `ai_chat`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `booking`
--
ALTER TABLE `booking`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `contact_messages`
--
ALTER TABLE `contact_messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `emergency_requests`
--
ALTER TABLE `emergency_requests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `feedback`
--
ALTER TABLE `feedback`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `feedbacks`
--
ALTER TABLE `feedbacks`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `payments`
--
ALTER TABLE `payments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `service`
--
ALTER TABLE `service`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `service_categories`
--
ALTER TABLE `service_categories`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `service_requests`
--
ALTER TABLE `service_requests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=22;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=45;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `booking`
--
ALTER TABLE `booking`
  ADD CONSTRAINT `booking_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `booking_ibfk_2` FOREIGN KEY (`technician_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `emergency_requests`
--
ALTER TABLE `emergency_requests`
  ADD CONSTRAINT `fk_emergency_customer` FOREIGN KEY (`customer_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `feedback`
--
ALTER TABLE `feedback`
  ADD CONSTRAINT `fk_feedback_customer` FOREIGN KEY (`customer_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_feedback_request` FOREIGN KEY (`service_request_id`) REFERENCES `service_requests` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `feedbacks`
--
ALTER TABLE `feedbacks`
  ADD CONSTRAINT `feedbacks_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `payments`
--
ALTER TABLE `payments`
  ADD CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`request_id`) REFERENCES `service_requests` (`id`);

--
-- Constraints for table `service_requests`
--
ALTER TABLE `service_requests`
  ADD CONSTRAINT `fk_customer` FOREIGN KEY (`customer_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_service` FOREIGN KEY (`service_id`) REFERENCES `service_categories` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_technician` FOREIGN KEY (`technician_id`) REFERENCES `users` (`id`) ON DELETE SET NULL;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
