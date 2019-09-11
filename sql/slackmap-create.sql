CREATE TABLE if not exists `slackmap` (
  `userid` int(11) NOT NULL,
  `slackid` varchar(12) NOT NULL,
  `workspaceid` varchar(12) NOT NULL,
  PRIMARY KEY (`userid`,`slackid`,`workspaceid`),
  KEY `sfk_awsuser` (`userid`),
  CONSTRAINT `sfk_awsuser` FOREIGN KEY (`userid`) REFERENCES `awsusers` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

alter table awsusers drop slackid;
