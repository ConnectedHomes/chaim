
/*
 * Users
 */

CREATE TABLE IF NOT EXISTS awsusers (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(127) NOT NULL,
    enabled enum('n','y') NOT NULL DEFAULT 'n',
    token VARCHAR(36) NULL,
    tokenexpires INTEGER NULL,
    lastslack INTEGER NULL DEFAULT 0,
    lastcli INTEGER NULL DEFAULT 0,
    lapsed int(11) DEFAULT 0,
    lapsedtm int(11) DEFAULT 0,
    slackid varchar(12) DEFAULT NULL,

    INDEX name_ind (name)
);
INSERT INTO awsusers SET name='chris.allison', enabled='y';

/*
 * AWS Accounts
 */

CREATE TABLE IF NOT EXISTS awsaccounts (
    id VARCHAR(12) NOT NULL,
    name VARCHAR(127) NOT NULL,

    UNIQUE INDEX id_ind (id)
);

/*
 * User groups/teams
 */

CREATE TABLE IF NOT EXISTS awsgroups (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(127) NOT NULL
);
INSERT INTO awsgroups SET name='SRE';

/*
 * AWS IAM Roles
 */

CREATE TABLE IF NOT EXISTS awsroles (
    id INTEGER PRIMARY KEY,
    name VARCHAR(30)
);
INSERT INTO awsroles SET id=10, name='CrossAccountReadOnly';
INSERT INTO awsroles SET id=50, name='CrossAccountPowerUser';
INSERT INTO awsroles SET id=80, name='CrossAccountSysAdmin';
INSERT INTO awsroles SET id=100, name='CrossAccountAdminUser';

/*
 * Group Account map (used for group privileges)
 */

CREATE TABLE IF NOT EXISTS groupaccountmap (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    accountid VARCHAR(12) NOT NULL,
    groupid INTEGER NOT NULL,

    CONSTRAINT fk_gmawsaccounts FOREIGN KEY (accountid)
    REFERENCES awsaccounts(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

    CONSTRAINT fk_gmawsgrps FOREIGN KEY (groupid)
    REFERENCES awsgroups(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

/*
 * User Group map
 */

CREATE TABLE IF NOT EXISTS groupusermap (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    groupid INTEGER NOT NULL,
    userid INTEGER NOT NULL,

    CONSTRAINT fk_guawsgroups FOREIGN KEY (groupid)
    REFERENCES awsgroups(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

    CONSTRAINT fk_guawsuser FOREIGN KEY (userid)
    REFERENCES awsusers(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

/*
 * Group IAM Role map (used for group privileges)
 */

CREATE TABLE IF NOT EXISTS grouprolemap (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    groupid INTEGER NOT NULL,
    roleid INTEGER NOT NULL,

    CONSTRAINT fk_grawsgroups FOREIGN KEY (groupid)
    REFERENCES awsgroups(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

    CONSTRAINT fk_grawsrole FOREIGN KEY (roleid)
    REFERENCES awsroles(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

/*
 * Key map
 */

CREATE TABLE IF NOT EXISTS keymap (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    userid INTEGER NOT NULL,
    accountid varchar(12) NOT NULL,
    accesskey varchar(20) NOT NULL,
    expires INTEGER NOT NULL,

    CONSTRAINT fk_kmawsaccount FOREIGN KEY (accountid)
    REFERENCES awsaccounts(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

    CONSTRAINT fk_kmawsuser FOREIGN KEY (userid)
    REFERENCES awsusers(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

/*
 *
 */

CREATE TABLE IF NOT EXISTS apiaccess (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    userid INTEGER NOT NULL,
    token varchar(36) NOT NULL,
    expires INTEGER NOT NULL,

    CONSTRAINT fk_aaawsuser FOREIGN KEY (userid)
    REFERENCES awsusers(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

/*
 * User permissions map
 */

CREATE TABLE IF NOT EXISTS useracctrolemap (
    accountid VARCHAR(12) NOT NULL,
    userid INTEGER NOT NULL,
    roleid INTEGER NOT NULL,

    CONSTRAINT ufk_awsaccounts FOREIGN KEY (accountid)
    REFERENCES awsaccounts(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

    CONSTRAINT ufk_awsuser FOREIGN KEY (userid)
    REFERENCES awsusers(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

    CONSTRAINT fk_awsrole FOREIGN KEY (roleid)
    REFERENCES awsroles(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

    PRIMARY KEY (accountid, userid, roleid)
);

/*
 * Group permissions map
 */

CREATE TABLE IF NOT EXISTS groupacctrolemap (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    accountid VARCHAR(12) NOT NULL,
    groupid INTEGER NOT NULL,
    roleid INTEGER NOT NULL,

    CONSTRAINT gar_awsaccounts FOREIGN KEY (accountid)
    REFERENCES awsaccounts(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

    CONSTRAINT garawsgroup FOREIGN KEY (groupid)
    REFERENCES awsgroups(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

    CONSTRAINT gar_awsrole FOREIGN KEY (roleid)
    REFERENCES awsroles(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);
