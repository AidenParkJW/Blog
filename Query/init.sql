DELETE FROM DJANGO_MIGRATIONS WHERE APP IN ('post', 'menu');

SELECT * INTO BLOG_MENU_BACK
FROM BLOG_MENU;

SELECT * INTO BLOG_POST_BACK 
FROM BLOG_POST;

DROP TABLE BLOG_POST;
DROP TABLE BLOG_MENU;

SET IDENTITY_INSERT [BLOG].[BLOG_MENU] ON;
INSERT INTO [BLOG].[BLOG_MENU]
           ([MENU_UID]
           ,[MENU_NAME]
           ,[MENU_DESC]
           ,[MENU_URL]
           ,[MENU_SORT_ORDER]
           ,[MENU_ISENABLED]
           ,[MENU_CRTE_DT]
           ,[MENU_MDFY_DT]
           ,[LFT]
           ,[RGHT]
           ,[TREE_ID]
           ,[LEVEL]
           ,[MENU_CRTE_USER_ID]
           ,[MENU_MDFY_USER_ID]
           ,[MENU_UP_UID]
           ,[SITE_ID])
SELECT      [MENU_UID] 
           ,[MENU_NAME]
           ,[MENU_DESC]
           ,[MENU_URL]
           ,[MENU_SORT_ORDER]
           ,[MENU_ISENABLED]
           ,[MENU_CRTE_DT]
           ,[MENU_MDFY_DT]
           ,[LFT]
           ,[RGHT]
           ,[TREE_ID]
           ,[LEVEL]
           ,[MENU_CRTE_USER_ID]
           ,[MENU_MDFY_USER_ID]
           ,[MENU_UP_UID]
           ,[SITE_ID]
FROM BLOG.BLOG_MENU_BACK;
SET IDENTITY_INSERT [BLOG].[BLOG_MENU] OFF


SET IDENTITY_INSERT [BLOG].[BLOG_POST] ON;
INSERT INTO [BLOG].[BLOG_POST]
           ([POST_UID]
           ,[POST_TITLE]
           ,[POST_SLUG]
           ,[POST_CONTENT]
           ,[POST_VIEWS]
           ,[POST_ISENABLED]
           ,[POST_TAG]
           ,[POST_CRTE_DT]
           ,[POST_MDFY_DT]
           ,[MENU_UID]
           ,[POST_CRTE_USER_ID]
           ,[POST_MDFY_USER_ID])
SELECT      [POST_UID]
           ,[POST_TITLE]
           ,[POST_SLUG]
           ,[POST_CONTENT]
           ,[POST_VIEWS]
           ,[POST_ISENABLED]
           ,[POST_TAG]
           ,[POST_CRTE_DT]
           ,[POST_MDFY_DT]
           ,[MENU_UID]
           ,[POST_CRTE_USER_ID]
           ,[POST_MDFY_USER_ID]
FROM [BLOG].[BLOG_POST_BACK];
SET IDENTITY_INSERT [BLOG].[BLOG_POST] OFF;
