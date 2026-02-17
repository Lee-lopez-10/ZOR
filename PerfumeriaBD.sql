USE [master]
GO
/****** Object:  Database [PerfumeriaDB]    Script Date: 10/2/2026 13:46:53 ******/
CREATE DATABASE [PerfumeriaDB]
 CONTAINMENT = NONE
 ON  PRIMARY 
( NAME = N'PerfumeriaDB', FILENAME = N'C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\PerfumeriaDB.mdf' , SIZE = 8192KB , MAXSIZE = UNLIMITED, FILEGROWTH = 65536KB )
 LOG ON 
( NAME = N'PerfumeriaDB_log', FILENAME = N'C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\PerfumeriaDB_log.ldf' , SIZE = 8192KB , MAXSIZE = 2048GB , FILEGROWTH = 65536KB )
 WITH CATALOG_COLLATION = DATABASE_DEFAULT, LEDGER = OFF
GO
ALTER DATABASE [PerfumeriaDB] SET COMPATIBILITY_LEVEL = 160
GO
IF (1 = FULLTEXTSERVICEPROPERTY('IsFullTextInstalled'))
begin
EXEC [PerfumeriaDB].[dbo].[sp_fulltext_database] @action = 'enable'
end
GO
ALTER DATABASE [PerfumeriaDB] SET ANSI_NULL_DEFAULT OFF 
GO
ALTER DATABASE [PerfumeriaDB] SET ANSI_NULLS OFF 
GO
ALTER DATABASE [PerfumeriaDB] SET ANSI_PADDING OFF 
GO
ALTER DATABASE [PerfumeriaDB] SET ANSI_WARNINGS OFF 
GO
ALTER DATABASE [PerfumeriaDB] SET ARITHABORT OFF 
GO
ALTER DATABASE [PerfumeriaDB] SET AUTO_CLOSE OFF 
GO
ALTER DATABASE [PerfumeriaDB] SET AUTO_SHRINK OFF 
GO
ALTER DATABASE [PerfumeriaDB] SET AUTO_UPDATE_STATISTICS ON 
GO
ALTER DATABASE [PerfumeriaDB] SET CURSOR_CLOSE_ON_COMMIT OFF 
GO
ALTER DATABASE [PerfumeriaDB] SET CURSOR_DEFAULT  GLOBAL 
GO
ALTER DATABASE [PerfumeriaDB] SET CONCAT_NULL_YIELDS_NULL OFF 
GO
ALTER DATABASE [PerfumeriaDB] SET NUMERIC_ROUNDABORT OFF 
GO
ALTER DATABASE [PerfumeriaDB] SET QUOTED_IDENTIFIER OFF 
GO
ALTER DATABASE [PerfumeriaDB] SET RECURSIVE_TRIGGERS OFF 
GO
ALTER DATABASE [PerfumeriaDB] SET  ENABLE_BROKER 
GO
ALTER DATABASE [PerfumeriaDB] SET AUTO_UPDATE_STATISTICS_ASYNC OFF 
GO
ALTER DATABASE [PerfumeriaDB] SET DATE_CORRELATION_OPTIMIZATION OFF 
GO
ALTER DATABASE [PerfumeriaDB] SET TRUSTWORTHY OFF 
GO
ALTER DATABASE [PerfumeriaDB] SET ALLOW_SNAPSHOT_ISOLATION OFF 
GO
ALTER DATABASE [PerfumeriaDB] SET PARAMETERIZATION SIMPLE 
GO
ALTER DATABASE [PerfumeriaDB] SET READ_COMMITTED_SNAPSHOT OFF 
GO
ALTER DATABASE [PerfumeriaDB] SET HONOR_BROKER_PRIORITY OFF 
GO
ALTER DATABASE [PerfumeriaDB] SET RECOVERY FULL 
GO
ALTER DATABASE [PerfumeriaDB] SET  MULTI_USER 
GO
ALTER DATABASE [PerfumeriaDB] SET PAGE_VERIFY CHECKSUM  
GO
ALTER DATABASE [PerfumeriaDB] SET DB_CHAINING OFF 
GO
ALTER DATABASE [PerfumeriaDB] SET FILESTREAM( NON_TRANSACTED_ACCESS = OFF ) 
GO
ALTER DATABASE [PerfumeriaDB] SET TARGET_RECOVERY_TIME = 60 SECONDS 
GO
ALTER DATABASE [PerfumeriaDB] SET DELAYED_DURABILITY = DISABLED 
GO
ALTER DATABASE [PerfumeriaDB] SET ACCELERATED_DATABASE_RECOVERY = OFF  
GO
EXEC sys.sp_db_vardecimal_storage_format N'PerfumeriaDB', N'ON'
GO
ALTER DATABASE [PerfumeriaDB] SET QUERY_STORE = ON
GO
ALTER DATABASE [PerfumeriaDB] SET QUERY_STORE (OPERATION_MODE = READ_WRITE, CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = 30), DATA_FLUSH_INTERVAL_SECONDS = 900, INTERVAL_LENGTH_MINUTES = 60, MAX_STORAGE_SIZE_MB = 1000, QUERY_CAPTURE_MODE = AUTO, SIZE_BASED_CLEANUP_MODE = AUTO, MAX_PLANS_PER_QUERY = 200, WAIT_STATS_CAPTURE_MODE = ON)
GO
USE [PerfumeriaDB]
GO
/****** Object:  Table [dbo].[Caja]    Script Date: 10/2/2026 13:46:53 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Caja](
	[ID_Caja] [int] IDENTITY(1,1) NOT NULL,
	[ID_Usuario] [int] NULL,
	[FechaApertura] [datetime] NULL,
	[MontoInicial] [decimal](10, 2) NOT NULL,
	[FechaCierre] [datetime] NULL,
	[MontoFinalSistema] [decimal](10, 2) NULL,
	[MontoFinalReal] [decimal](10, 2) NULL,
	[Diferencia] [decimal](10, 2) NULL,
	[Estado] [varchar](20) NULL,
PRIMARY KEY CLUSTERED 
(
	[ID_Caja] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Categoria]    Script Date: 10/2/2026 13:46:53 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Categoria](
	[ID_Categoria] [int] IDENTITY(1,1) NOT NULL,
	[Nombre] [varchar](100) NOT NULL,
	[Descripcion] [varchar](255) NULL,
PRIMARY KEY CLUSTERED 
(
	[ID_Categoria] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Cliente]    Script Date: 10/2/2026 13:46:53 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Cliente](
	[ID_Cliente] [int] IDENTITY(1,1) NOT NULL,
	[Nombre] [varchar](100) NOT NULL,
	[Telefono] [varchar](20) NULL,
	[Email] [varchar](100) NULL,
	[TotalComprado] [decimal](10, 2) NULL,
	[FechaRegistro] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[ID_Cliente] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DetallePedido]    Script Date: 10/2/2026 13:46:53 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DetallePedido](
	[ID_Detalle] [int] IDENTITY(1,1) NOT NULL,
	[ID_Pedido] [int] NULL,
	[ID_Producto] [int] NULL,
	[Cantidad] [int] NOT NULL,
	[PrecioUnitario] [decimal](10, 2) NOT NULL,
	[ID_Perfume] [int] NULL,
PRIMARY KEY CLUSTERED 
(
	[ID_Detalle] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[EntradaInventario]    Script Date: 10/2/2026 13:46:53 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[EntradaInventario](
	[ID_Entrada] [int] IDENTITY(1,1) NOT NULL,
	[ID_Producto] [int] NULL,
	[Cantidad] [int] NOT NULL,
	[CostoUnitario] [decimal](10, 2) NULL,
	[CostoEnvio] [decimal](10, 2) NULL,
	[FechaEntrada] [datetime] NULL,
	[ID_Usuario] [int] NULL,
	[ID_Perfume] [int] NULL,
PRIMARY KEY CLUSTERED 
(
	[ID_Entrada] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Gasto]    Script Date: 10/2/2026 13:46:53 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Gasto](
	[ID_Gasto] [int] IDENTITY(1,1) NOT NULL,
	[Descripcion] [varchar](255) NOT NULL,
	[Monto] [decimal](10, 2) NOT NULL,
	[Fecha] [datetime] NULL,
	[ID_Usuario] [int] NULL,
PRIMARY KEY CLUSTERED 
(
	[ID_Gasto] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Pedido]    Script Date: 10/2/2026 13:46:53 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Pedido](
	[ID_Pedido] [int] IDENTITY(1,1) NOT NULL,
	[ID_Usuario] [int] NULL,
	[ID_Cliente] [int] NULL,
	[FechaPedido] [datetime] NULL,
	[Total] [decimal](10, 2) NULL,
	[Descuento] [decimal](10, 2) NULL,
	[Estado] [varchar](50) NULL,
PRIMARY KEY CLUSTERED 
(
	[ID_Pedido] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Perfume]    Script Date: 10/2/2026 13:46:53 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Perfume](
	[ID_Perfume] [int] IDENTITY(1,1) NOT NULL,
	[Nombre] [varchar](100) NOT NULL,
	[Marca] [varchar](100) NOT NULL,
	[Descripcion] [varchar](255) NULL,
	[Precio] [decimal](10, 2) NOT NULL,
	[Stock] [int] NOT NULL,
	[Genero] [varchar](20) NULL,
	[Mililitros] [int] NULL,
	[Imagen] [varchar](255) NULL,
	[Estado] [bit] NULL,
PRIMARY KEY CLUSTERED 
(
	[ID_Perfume] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Producto]    Script Date: 10/2/2026 13:46:53 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Producto](
	[ID_Producto] [int] IDENTITY(1,1) NOT NULL,
	[Nombre] [varchar](150) NOT NULL,
	[Descripcion] [text] NULL,
	[Precio] [decimal](10, 2) NOT NULL,
	[Stock] [int] NOT NULL,
	[ID_Categoria] [int] NULL,
	[ID_Proveedor] [int] NULL,
	[ImagenURL] [varchar](max) NULL,
PRIMARY KEY CLUSTERED 
(
	[ID_Producto] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Proveedor]    Script Date: 10/2/2026 13:46:53 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Proveedor](
	[ID_Proveedor] [int] IDENTITY(1,1) NOT NULL,
	[NombreEmpresa] [varchar](150) NOT NULL,
	[Contacto] [varchar](100) NULL,
	[Telefono] [varchar](20) NULL,
PRIMARY KEY CLUSTERED 
(
	[ID_Proveedor] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Rol]    Script Date: 10/2/2026 13:46:53 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Rol](
	[ID_Rol] [int] IDENTITY(1,1) NOT NULL,
	[NombreRol] [varchar](50) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[ID_Rol] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usuario]    Script Date: 10/2/2026 13:46:53 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usuario](
	[ID_Usuario] [int] IDENTITY(1,1) NOT NULL,
	[Nombre] [varchar](100) NOT NULL,
	[Email] [varchar](100) NOT NULL,
	[Contrasena] [varchar](255) NOT NULL,
	[ID_Rol] [int] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[ID_Usuario] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
SET IDENTITY_INSERT [dbo].[Caja] ON 
GO
INSERT [dbo].[Caja] ([ID_Caja], [ID_Usuario], [FechaApertura], [MontoInicial], [FechaCierre], [MontoFinalSistema], [MontoFinalReal], [Diferencia], [Estado]) VALUES (1, 2, CAST(N'2026-02-05T14:19:28.543' AS DateTime), CAST(65.50 AS Decimal(10, 2)), CAST(N'2026-02-05T14:19:36.470' AS DateTime), CAST(65.50 AS Decimal(10, 2)), CAST(50.00 AS Decimal(10, 2)), CAST(-15.50 AS Decimal(10, 2)), N'Cerrada')
GO
SET IDENTITY_INSERT [dbo].[Caja] OFF
GO
SET IDENTITY_INSERT [dbo].[Categoria] ON 
GO
INSERT [dbo].[Categoria] ([ID_Categoria], [Nombre], [Descripcion]) VALUES (1, N'Dama', NULL)
GO
INSERT [dbo].[Categoria] ([ID_Categoria], [Nombre], [Descripcion]) VALUES (2, N'Caballero', NULL)
GO
INSERT [dbo].[Categoria] ([ID_Categoria], [Nombre], [Descripcion]) VALUES (3, N'Unisex', NULL)
GO
INSERT [dbo].[Categoria] ([ID_Categoria], [Nombre], [Descripcion]) VALUES (4, N'Infantil', NULL)
GO
SET IDENTITY_INSERT [dbo].[Categoria] OFF
GO
SET IDENTITY_INSERT [dbo].[Cliente] ON 
GO
INSERT [dbo].[Cliente] ([ID_Cliente], [Nombre], [Telefono], [Email], [TotalComprado], [FechaRegistro]) VALUES (1, N'Público General', N'00000000', N'anonimo@cliente.com', CAST(0.00 AS Decimal(10, 2)), CAST(N'2026-02-03T14:15:24.830' AS DateTime))
GO
INSERT [dbo].[Cliente] ([ID_Cliente], [Nombre], [Telefono], [Email], [TotalComprado], [FechaRegistro]) VALUES (2, N'Andrea Valle', N'1231995+', N'', CAST(90.00 AS Decimal(10, 2)), CAST(N'2026-02-07T19:11:27.133' AS DateTime))
GO
INSERT [dbo].[Cliente] ([ID_Cliente], [Nombre], [Telefono], [Email], [TotalComprado], [FechaRegistro]) VALUES (3, N'555', N'', N'', CAST(0.00 AS Decimal(10, 2)), CAST(N'2026-02-07T19:32:11.510' AS DateTime))
GO
INSERT [dbo].[Cliente] ([ID_Cliente], [Nombre], [Telefono], [Email], [TotalComprado], [FechaRegistro]) VALUES (4, N'Andrea Lucia', N'', N'', CAST(200.00 AS Decimal(10, 2)), CAST(N'2026-02-07T19:32:28.790' AS DateTime))
GO
INSERT [dbo].[Cliente] ([ID_Cliente], [Nombre], [Telefono], [Email], [TotalComprado], [FechaRegistro]) VALUES (5, N'55', N'', N'', CAST(0.00 AS Decimal(10, 2)), CAST(N'2026-02-07T19:37:13.330' AS DateTime))
GO
INSERT [dbo].[Cliente] ([ID_Cliente], [Nombre], [Telefono], [Email], [TotalComprado], [FechaRegistro]) VALUES (6, N'andrea', N'123456789', N'andrea@12.com', CAST(150.00 AS Decimal(10, 2)), CAST(N'2026-02-07T19:46:53.573' AS DateTime))
GO
INSERT [dbo].[Cliente] ([ID_Cliente], [Nombre], [Telefono], [Email], [TotalComprado], [FechaRegistro]) VALUES (7, N'ANDREA', N'12345678', N'', CAST(150.00 AS Decimal(10, 2)), CAST(N'2026-02-07T19:51:29.350' AS DateTime))
GO
INSERT [dbo].[Cliente] ([ID_Cliente], [Nombre], [Telefono], [Email], [TotalComprado], [FechaRegistro]) VALUES (8, N'JUAN', N'12345678', N'', CAST(132.30 AS Decimal(10, 2)), CAST(N'2026-02-09T14:30:26.450' AS DateTime))
GO
SET IDENTITY_INSERT [dbo].[Cliente] OFF
GO
SET IDENTITY_INSERT [dbo].[DetallePedido] ON 
GO
INSERT [dbo].[DetallePedido] ([ID_Detalle], [ID_Pedido], [ID_Producto], [Cantidad], [PrecioUnitario], [ID_Perfume]) VALUES (1, 5, NULL, 1, CAST(90.00 AS Decimal(10, 2)), 5)
GO
INSERT [dbo].[DetallePedido] ([ID_Detalle], [ID_Pedido], [ID_Producto], [Cantidad], [PrecioUnitario], [ID_Perfume]) VALUES (2, 6, NULL, 2, CAST(100.00 AS Decimal(10, 2)), 10)
GO
INSERT [dbo].[DetallePedido] ([ID_Detalle], [ID_Pedido], [ID_Producto], [Cantidad], [PrecioUnitario], [ID_Perfume]) VALUES (3, 7, NULL, 1, CAST(150.00 AS Decimal(10, 2)), 13)
GO
INSERT [dbo].[DetallePedido] ([ID_Detalle], [ID_Pedido], [ID_Producto], [Cantidad], [PrecioUnitario], [ID_Perfume]) VALUES (4, 8, NULL, 1, CAST(150.00 AS Decimal(10, 2)), 13)
GO
INSERT [dbo].[DetallePedido] ([ID_Detalle], [ID_Pedido], [ID_Producto], [Cantidad], [PrecioUnitario], [ID_Perfume]) VALUES (5, 9, NULL, 1, CAST(150.00 AS Decimal(10, 2)), 13)
GO
INSERT [dbo].[DetallePedido] ([ID_Detalle], [ID_Pedido], [ID_Producto], [Cantidad], [PrecioUnitario], [ID_Perfume]) VALUES (6, 10, NULL, 1, CAST(147.00 AS Decimal(10, 2)), 19)
GO
SET IDENTITY_INSERT [dbo].[DetallePedido] OFF
GO
SET IDENTITY_INSERT [dbo].[Pedido] ON 
GO
INSERT [dbo].[Pedido] ([ID_Pedido], [ID_Usuario], [ID_Cliente], [FechaPedido], [Total], [Descuento], [Estado]) VALUES (5, 2, 2, CAST(N'2026-02-07T19:25:20.977' AS DateTime), CAST(90.00 AS Decimal(10, 2)), CAST(0.00 AS Decimal(10, 2)), N'Pagado')
GO
INSERT [dbo].[Pedido] ([ID_Pedido], [ID_Usuario], [ID_Cliente], [FechaPedido], [Total], [Descuento], [Estado]) VALUES (6, 2, 4, CAST(N'2026-02-07T19:32:50.030' AS DateTime), CAST(200.00 AS Decimal(10, 2)), CAST(0.00 AS Decimal(10, 2)), N'Pagado')
GO
INSERT [dbo].[Pedido] ([ID_Pedido], [ID_Usuario], [ID_Cliente], [FechaPedido], [Total], [Descuento], [Estado]) VALUES (7, 2, 6, CAST(N'2026-02-07T19:46:58.377' AS DateTime), CAST(150.00 AS Decimal(10, 2)), CAST(0.00 AS Decimal(10, 2)), N'Pagado')
GO
INSERT [dbo].[Pedido] ([ID_Pedido], [ID_Usuario], [ID_Cliente], [FechaPedido], [Total], [Descuento], [Estado]) VALUES (8, 2, 7, CAST(N'2026-02-07T19:51:35.360' AS DateTime), CAST(150.00 AS Decimal(10, 2)), CAST(0.00 AS Decimal(10, 2)), N'Pagado')
GO
INSERT [dbo].[Pedido] ([ID_Pedido], [ID_Usuario], [ID_Cliente], [FechaPedido], [Total], [Descuento], [Estado]) VALUES (9, 2, 1, CAST(N'2026-02-09T14:26:55.400' AS DateTime), CAST(150.00 AS Decimal(10, 2)), CAST(0.00 AS Decimal(10, 2)), N'Pagado')
GO
INSERT [dbo].[Pedido] ([ID_Pedido], [ID_Usuario], [ID_Cliente], [FechaPedido], [Total], [Descuento], [Estado]) VALUES (10, 2, 8, CAST(N'2026-02-09T14:30:40.757' AS DateTime), CAST(132.30 AS Decimal(10, 2)), CAST(14.70 AS Decimal(10, 2)), N'Pagado')
GO
SET IDENTITY_INSERT [dbo].[Pedido] OFF
GO
SET IDENTITY_INSERT [dbo].[Perfume] ON 
GO
INSERT [dbo].[Perfume] ([ID_Perfume], [Nombre], [Marca], [Descripcion], [Precio], [Stock], [Genero], [Mililitros], [Imagen], [Estado]) VALUES (1, N'Sauvage', N'Dior', N'Fragancia fresca y amaderada', CAST(120.00 AS Decimal(10, 2)), 20, N'Hombre', 100, N'img/perfumes/dior_sauvage.webp', 1)
GO
INSERT [dbo].[Perfume] ([ID_Perfume], [Nombre], [Marca], [Descripcion], [Precio], [Stock], [Genero], [Mililitros], [Imagen], [Estado]) VALUES (2, N'Chanel N°5', N'Chanel', N'Clásico elegante floral', CAST(150.00 AS Decimal(10, 2)), 15, N'Mujer', 100, N'img/perfumes/chanel_no5.jpg', 1)
GO
INSERT [dbo].[Perfume] ([ID_Perfume], [Nombre], [Marca], [Descripcion], [Precio], [Stock], [Genero], [Mililitros], [Imagen], [Estado]) VALUES (3, N'Eros', N'Versace', N'Aroma intenso y seductor', CAST(110.00 AS Decimal(10, 2)), 18, N'Hombre', 100, N'img/perfumes/versace_eros.webp', 1)
GO
INSERT [dbo].[Perfume] ([ID_Perfume], [Nombre], [Marca], [Descripcion], [Precio], [Stock], [Genero], [Mililitros], [Imagen], [Estado]) VALUES (4, N'La Vie Est Belle', N'Lancôme', N'Fragancia dulce y sofisticada', CAST(135.00 AS Decimal(10, 2)), 12, N'Mujer', 75, N'img/perfumes/la_vie_est_belle.webp', 1)
GO
INSERT [dbo].[Perfume] ([ID_Perfume], [Nombre], [Marca], [Descripcion], [Precio], [Stock], [Genero], [Mililitros], [Imagen], [Estado]) VALUES (5, N'CK One', N'Calvin Klein', N'Fragancia cítrica y fresca', CAST(90.00 AS Decimal(10, 2)), 24, N'Unisex', 100, N'img/perfumes/ck_one.jpg', 1)
GO
INSERT [dbo].[Perfume] ([ID_Perfume], [Nombre], [Marca], [Descripcion], [Precio], [Stock], [Genero], [Mililitros], [Imagen], [Estado]) VALUES (7, N'Coco Mademoiselle', N'Chanel', NULL, CAST(220.00 AS Decimal(10, 2)), 10, N'Damas', 100, N'img/perfumes/chanel_coco_mademoiselle.avif', 1)
GO
INSERT [dbo].[Perfume] ([ID_Perfume], [Nombre], [Marca], [Descripcion], [Precio], [Stock], [Genero], [Mililitros], [Imagen], [Estado]) VALUES (8, N'Good Girl Blush Elixir', N'Carolina Herrera', NULL, CAST(160.00 AS Decimal(10, 2)), 10, N'Damas', 80, N'img/perfumes/good_girl_blush_elixir.webp', 1)
GO
INSERT [dbo].[Perfume] ([ID_Perfume], [Nombre], [Marca], [Descripcion], [Precio], [Stock], [Genero], [Mililitros], [Imagen], [Estado]) VALUES (9, N'Very Good Girl', N'Carolina Herrera', NULL, CAST(90.00 AS Decimal(10, 2)), 10, N'Damas', 80, N'img/perfumes/very_good_girl.jpg', 1)
GO
INSERT [dbo].[Perfume] ([ID_Perfume], [Nombre], [Marca], [Descripcion], [Precio], [Stock], [Genero], [Mililitros], [Imagen], [Estado]) VALUES (10, N'Eros Pour Femme', N'Versace', NULL, CAST(100.00 AS Decimal(10, 2)), 8, N'Damas', 100, N'img/perfumes/eros_pour_femme.webp', 1)
GO
INSERT [dbo].[Perfume] ([ID_Perfume], [Nombre], [Marca], [Descripcion], [Precio], [Stock], [Genero], [Mililitros], [Imagen], [Estado]) VALUES (11, N'Crystal Noir', N'Versace', NULL, CAST(150.00 AS Decimal(10, 2)), 10, N'Damas', 90, N'img/perfumes/crystal_noir.webp', 1)
GO
INSERT [dbo].[Perfume] ([ID_Perfume], [Nombre], [Marca], [Descripcion], [Precio], [Stock], [Genero], [Mililitros], [Imagen], [Estado]) VALUES (12, N'Her', N'Burberry', NULL, CAST(90.00 AS Decimal(10, 2)), 10, N'Damas', 100, N'img/perfumes/burberry_her.webp', 1)
GO
INSERT [dbo].[Perfume] ([ID_Perfume], [Nombre], [Marca], [Descripcion], [Precio], [Stock], [Genero], [Mililitros], [Imagen], [Estado]) VALUES (13, N'Bright Crystal Absolu', N'Versace', NULL, CAST(150.00 AS Decimal(10, 2)), 7, N'Damas', 100, N'img/perfumes/bright_crystal_absolu.webp', 1)
GO
INSERT [dbo].[Perfume] ([ID_Perfume], [Nombre], [Marca], [Descripcion], [Precio], [Stock], [Genero], [Mililitros], [Imagen], [Estado]) VALUES (14, N'Toy 2 Bubble Gum', N'Moschino', NULL, CAST(100.00 AS Decimal(10, 2)), 10, N'Damas', 100, N'img/perfumes/toy2_bubblegum.jpg', 1)
GO
INSERT [dbo].[Perfume] ([ID_Perfume], [Nombre], [Marca], [Descripcion], [Precio], [Stock], [Genero], [Mililitros], [Imagen], [Estado]) VALUES (15, N'Good Girl Blush', N'Carolina Herrera', NULL, CAST(100.00 AS Decimal(10, 2)), 10, N'Damas', 80, N'img/perfumes/good_girl_blush.webp', 1)
GO
INSERT [dbo].[Perfume] ([ID_Perfume], [Nombre], [Marca], [Descripcion], [Precio], [Stock], [Genero], [Mililitros], [Imagen], [Estado]) VALUES (16, N'Rose Goldea', N'Bvlgari', NULL, CAST(115.00 AS Decimal(10, 2)), 10, N'Damas', 90, N'img/perfumes/rose_goldea.jpg', 1)
GO
INSERT [dbo].[Perfume] ([ID_Perfume], [Nombre], [Marca], [Descripcion], [Precio], [Stock], [Genero], [Mililitros], [Imagen], [Estado]) VALUES (17, N'Bleu', N'Chanel', NULL, CAST(140.00 AS Decimal(10, 2)), 10, N'Caballeros', 100, N'img/perfumes/chanel_bleu.png', 1)
GO
INSERT [dbo].[Perfume] ([ID_Perfume], [Nombre], [Marca], [Descripcion], [Precio], [Stock], [Genero], [Mililitros], [Imagen], [Estado]) VALUES (18, N'Eros', N'Versace', NULL, CAST(45.00 AS Decimal(10, 2)), 10, N'Caballeros', 100, N'img/perfumes/versace_eros.webp', 1)
GO
INSERT [dbo].[Perfume] ([ID_Perfume], [Nombre], [Marca], [Descripcion], [Precio], [Stock], [Genero], [Mililitros], [Imagen], [Estado]) VALUES (19, N'Sauvage', N'Dior', NULL, CAST(147.00 AS Decimal(10, 2)), 9, N'Caballeros', 100, N'img/perfumes/dior_sauvage.webp', 1)
GO
INSERT [dbo].[Perfume] ([ID_Perfume], [Nombre], [Marca], [Descripcion], [Precio], [Stock], [Genero], [Mililitros], [Imagen], [Estado]) VALUES (20, N'Sauvage Elixir', N'Dior', NULL, CAST(240.00 AS Decimal(10, 2)), 10, N'Caballeros', 60, N'img/perfumes/dior_sauvage_elixir.webp', 1)
GO
INSERT [dbo].[Perfume] ([ID_Perfume], [Nombre], [Marca], [Descripcion], [Precio], [Stock], [Genero], [Mililitros], [Imagen], [Estado]) VALUES (21, N'212 Men Sexy', N'Carolina Herrera', NULL, CAST(77.00 AS Decimal(10, 2)), 10, N'Caballeros', 100, N'img/perfumes/212_men_sexy.webp', 1)
GO
INSERT [dbo].[Perfume] ([ID_Perfume], [Nombre], [Marca], [Descripcion], [Precio], [Stock], [Genero], [Mililitros], [Imagen], [Estado]) VALUES (22, N'One Million Royal', N'Paco Rabanne', NULL, CAST(120.00 AS Decimal(10, 2)), 10, N'Caballeros', 100, N'img/perfumes/one_million_royal.webp', 1)
GO
SET IDENTITY_INSERT [dbo].[Perfume] OFF
GO
SET IDENTITY_INSERT [dbo].[Proveedor] ON 
GO
INSERT [dbo].[Proveedor] ([ID_Proveedor], [NombreEmpresa], [Contacto], [Telefono]) VALUES (1, N'JUSPIT WHOLE MIAMI', NULL, N'626 8707803')
GO
SET IDENTITY_INSERT [dbo].[Proveedor] OFF
GO
SET IDENTITY_INSERT [dbo].[Rol] ON 
GO
INSERT [dbo].[Rol] ([ID_Rol], [NombreRol]) VALUES (1, N'Administrador')
GO
INSERT [dbo].[Rol] ([ID_Rol], [NombreRol]) VALUES (2, N'Vendedor')
GO
SET IDENTITY_INSERT [dbo].[Rol] OFF
GO
SET IDENTITY_INSERT [dbo].[Usuario] ON 
GO
INSERT [dbo].[Usuario] ([ID_Usuario], [Nombre], [Email], [Contrasena], [ID_Rol]) VALUES (1, N'Administrador Principal', N'edu2355g@gmail.com', N'admin123', 1)
GO
INSERT [dbo].[Usuario] ([ID_Usuario], [Nombre], [Email], [Contrasena], [ID_Rol]) VALUES (2, N'Vendedor Turno', N'vendedor@gmail.com', N'123', 2)
GO
SET IDENTITY_INSERT [dbo].[Usuario] OFF
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [UQ__Usuario__A9D1053491B07FBA]    Script Date: 10/2/2026 13:46:53 ******/
ALTER TABLE [dbo].[Usuario] ADD UNIQUE NONCLUSTERED 
(
	[Email] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
ALTER TABLE [dbo].[Caja] ADD  DEFAULT (getdate()) FOR [FechaApertura]
GO
ALTER TABLE [dbo].[Caja] ADD  DEFAULT ('Abierta') FOR [Estado]
GO
ALTER TABLE [dbo].[Cliente] ADD  DEFAULT ((0)) FOR [TotalComprado]
GO
ALTER TABLE [dbo].[Cliente] ADD  DEFAULT (getdate()) FOR [FechaRegistro]
GO
ALTER TABLE [dbo].[EntradaInventario] ADD  DEFAULT ((0)) FOR [CostoEnvio]
GO
ALTER TABLE [dbo].[EntradaInventario] ADD  DEFAULT (getdate()) FOR [FechaEntrada]
GO
ALTER TABLE [dbo].[Gasto] ADD  DEFAULT (getdate()) FOR [Fecha]
GO
ALTER TABLE [dbo].[Pedido] ADD  DEFAULT (getdate()) FOR [FechaPedido]
GO
ALTER TABLE [dbo].[Pedido] ADD  DEFAULT ((0)) FOR [Descuento]
GO
ALTER TABLE [dbo].[Perfume] ADD  CONSTRAINT [DF_Perfume_Stock]  DEFAULT ((10)) FOR [Stock]
GO
ALTER TABLE [dbo].[Perfume] ADD  DEFAULT ((1)) FOR [Estado]
GO
ALTER TABLE [dbo].[Caja]  WITH CHECK ADD FOREIGN KEY([ID_Usuario])
REFERENCES [dbo].[Usuario] ([ID_Usuario])
GO
ALTER TABLE [dbo].[DetallePedido]  WITH CHECK ADD FOREIGN KEY([ID_Pedido])
REFERENCES [dbo].[Pedido] ([ID_Pedido])
GO
ALTER TABLE [dbo].[DetallePedido]  WITH CHECK ADD FOREIGN KEY([ID_Producto])
REFERENCES [dbo].[Producto] ([ID_Producto])
GO
ALTER TABLE [dbo].[DetallePedido]  WITH CHECK ADD  CONSTRAINT [FK_DetallePedido_Perfume] FOREIGN KEY([ID_Perfume])
REFERENCES [dbo].[Perfume] ([ID_Perfume])
GO
ALTER TABLE [dbo].[DetallePedido] CHECK CONSTRAINT [FK_DetallePedido_Perfume]
GO
ALTER TABLE [dbo].[EntradaInventario]  WITH CHECK ADD FOREIGN KEY([ID_Producto])
REFERENCES [dbo].[Producto] ([ID_Producto])
GO
ALTER TABLE [dbo].[EntradaInventario]  WITH CHECK ADD FOREIGN KEY([ID_Usuario])
REFERENCES [dbo].[Usuario] ([ID_Usuario])
GO
ALTER TABLE [dbo].[EntradaInventario]  WITH CHECK ADD  CONSTRAINT [FK_EntradaInventario_Perfume] FOREIGN KEY([ID_Perfume])
REFERENCES [dbo].[Perfume] ([ID_Perfume])
GO
ALTER TABLE [dbo].[EntradaInventario] CHECK CONSTRAINT [FK_EntradaInventario_Perfume]
GO
ALTER TABLE [dbo].[Gasto]  WITH CHECK ADD FOREIGN KEY([ID_Usuario])
REFERENCES [dbo].[Usuario] ([ID_Usuario])
GO
ALTER TABLE [dbo].[Pedido]  WITH CHECK ADD FOREIGN KEY([ID_Cliente])
REFERENCES [dbo].[Cliente] ([ID_Cliente])
GO
ALTER TABLE [dbo].[Pedido]  WITH CHECK ADD FOREIGN KEY([ID_Usuario])
REFERENCES [dbo].[Usuario] ([ID_Usuario])
GO
ALTER TABLE [dbo].[Producto]  WITH CHECK ADD FOREIGN KEY([ID_Categoria])
REFERENCES [dbo].[Categoria] ([ID_Categoria])
GO
ALTER TABLE [dbo].[Producto]  WITH CHECK ADD FOREIGN KEY([ID_Proveedor])
REFERENCES [dbo].[Proveedor] ([ID_Proveedor])
GO
ALTER TABLE [dbo].[Usuario]  WITH CHECK ADD FOREIGN KEY([ID_Rol])
REFERENCES [dbo].[Rol] ([ID_Rol])
GO
USE [master]
GO
ALTER DATABASE [PerfumeriaDB] SET  READ_WRITE 
GO

USE PerfumeriaDB;
GO

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Perfume')
BEGIN
    CREATE TABLE dbo.Perfume (
        ID_Perfume INT IDENTITY(1,1) PRIMARY KEY,
        Nombre VARCHAR(100) NOT NULL,
        Marca VARCHAR(100) NOT NULL,
        Descripcion VARCHAR(255) NULL,
        Precio DECIMAL(10,2) NOT NULL,
        Stock INT NOT NULL DEFAULT 10,
        Genero VARCHAR(20) NOT NULL CHECK (Genero IN ('Dama','Caballero','Unisex')),
        Mililitros INT NULL,
        Imagen VARCHAR(255) NULL,
        Estado BIT NOT NULL DEFAULT 1
    );
END
GO

INSERT INTO Perfume
(Nombre, Marca, Descripcion, Precio, Stock, Genero, Mililitros, Imagen, Estado)
VALUES
('Chanel N°5', 'Chanel', 'Clásico elegante floral', 150.00, 15, 'Dama', 100, 'img/perfumes/chanel_no5.jpg', 1),
('La Vie Est Belle', 'Lancôme', 'Fragancia dulce y sofisticada', 135.00, 12, 'Dama', 75, 'img/perfumes/la_vie_est_belle.webp', 1),
('Coco Mademoiselle', 'Chanel', NULL, 220.00, 10, 'Dama', 100, 'img/perfumes/chanel_coco_mademoiselle.avif', 1),
('Good Girl Blush Elixir', 'Carolina Herrera', NULL, 160.00, 10, 'Dama', 80, 'img/perfumes/good_girl_blush_elixir.webp', 1),
('Very Good Girl', 'Carolina Herrera', NULL, 90.00, 10, 'Dama', 80, 'img/perfumes/very_good_girl.jpg', 1),
('Eros Pour Femme', 'Versace', NULL, 100.00, 8, 'Dama', 100, 'img/perfumes/eros_pour_femme.webp', 1),
('Crystal Noir', 'Versace', NULL, 150.00, 10, 'Dama', 90, 'img/perfumes/crystal_noir.webp', 1),
('Her', 'Burberry', NULL, 90.00, 10, 'Dama', 100, 'img/perfumes/burberry_her.webp', 1),
('Bright Crystal Absolu', 'Versace', NULL, 150.00, 7, 'Dama', 100, 'img/perfumes/bright_crystal_absolu.webp', 1),
('Toy 2 Bubble Gum', 'Moschino', NULL, 100.00, 10, 'Dama', 100, 'img/perfumes/toy2_bubblegum.jpg', 1),
('Good Girl Blush', 'Carolina Herrera', NULL, 100.00, 10, 'Dama', 80, 'img/perfumes/good_girl_blush.webp', 1),
('Rose Goldea', 'Bvlgari', NULL, 115.00, 10, 'Dama', 90, 'img/perfumes/rose_goldea.jpg', 1);
GO

INSERT INTO Perfume
(Nombre, Marca, Descripcion, Precio, Stock, Genero, Mililitros, Imagen, Estado)
VALUES
('Sauvage', 'Dior', 'Fragancia fresca y amaderada', 120.00, 20, 'Caballero', 100, 'img/perfumes/dior_sauvage.webp', 1),
('Eros', 'Versace', 'Aroma intenso y seductor', 110.00, 18, 'Caballero', 100, 'img/perfumes/versace_eros.webp', 1),
('Bleu', 'Chanel', NULL, 140.00, 10, 'Caballero', 100, 'img/perfumes/chanel_bleu.png', 1),
('Sauvage Elixir', 'Dior', NULL, 240.00, 10, 'Caballero', 60, 'img/perfumes/dior_sauvage_elixir.webp', 1),
('212 Men Sexy', 'Carolina Herrera', NULL, 77.00, 10, 'Caballero', 100, 'img/perfumes/212_men_sexy.webp', 1),
('One Million Royal', 'Paco Rabanne', NULL, 120.00, 10, 'Caballero', 100, 'img/perfumes/one_million_royal.webp', 1);
GO

INSERT INTO Perfume
(Nombre, Marca, Descripcion, Precio, Stock, Genero, Mililitros, Imagen, Estado)
VALUES
('CK One', 'Calvin Klein', 'Fragancia cítrica y fresca', 90.00, 24, 'Unisex', 100, 'img/perfumes/ck_one.jpg', 1);
GO
