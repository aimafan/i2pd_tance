#include "MySQLConnector.h"



// 将 std::tm 转换为 SQLString
sql::SQLString tmToSQLString(const std::tm* tmInfo) {
    stringstream ss;
    ss << std::put_time(tmInfo, "%Y-%m-%d %H:%M:%S");
    return ss.str();
}

MySQLConnector::MySQLConnector(const string& host, const string& user, const string& password)
    : host_(host), user_(user), password_(password) {
    driver_ = sql::mysql::get_mysql_driver_instance();
    connect();
    createDatabase("darknet");
}

MySQLConnector::~MySQLConnector() {
    delete con_;
}

void MySQLConnector::connect() {
    con_ = driver_->connect(host_, user_, password_);
    createLeaseSetsTable();
    createRouterinfoTable();
}

void MySQLConnector::createDatabase(const string& dbName) {
    sql::Statement *stmt = con_->createStatement();
    stmt->execute("CREATE DATABASE IF NOT EXISTS " + dbName);
    delete stmt;
    con_->setSchema(dbName);
}

void MySQLConnector::createRouterinfoTable() {
    sql::Statement *stmt = con_->createStatement();
    stmt->execute("USE darknet"); 
    stmt->execute("CREATE TABLE IF NOT EXISTS RouterInfo ("
                      "hash VARCHAR(64) PRIMARY KEY, "
                      "isFFpeers BOOLEAN,"
                      "caps VARCHAR(6),"
                      "version VARCHAR(6),"
                      "netId VARCHAR(2),"
                      "published_time DATETIME,"
                      "updatetime DATETIME,"
                      "crytokeytype VARCHAR(50),"
                      "signkey VARCHAR(25),"
                      "NTCP2_ipv4 VARCHAR(20),"
                      "NTCP2_ipv4_port INT,"
                      "NTCP2_s VARCHAR(64),"
                      "NTCP2_i VARCHAR(32),"
                      "NTCP2_ipv6 VARCHAR(45),"
                      "NTCP2_ipv6_port INT,"
                      "SSU_ipv4 VARCHAR(20),"
                      "SSU_ipv4_port INT,"
                      "SSU_ipv6 VARCHAR(45),"
                      "SSU_ipv6_port INT"
                      ")");
    delete stmt;
}


// 存储LeaseSets
void MySQLConnector::createLeaseSetsTable() {
    sql::Statement *stmt = con_->createStatement();
    stmt->execute("USE darknet");
    stmt->execute("CREATE TABLE IF NOT EXISTS LeaseSets ("
                      "hash VARCHAR(128) PRIMARY KEY, "
                      "encryption_type VARCHAR(64), "
                      "expiration_time DATETIME, "
                      "storage_type VARCHAR(50), "
                      "published_time DATETIME, "
                      "updatetime DATETIME, "
                      "query_method VARCHAR(50)"
                      ")");
    
    stmt->execute("CREATE TABLE IF NOT EXISTS Leases ("
                      "lease_id INT AUTO_INCREMENT PRIMARY KEY, "
                      "router_hash VARCHAR(128), "
                      "gateway_address VARCHAR(128), "
                      "tunnel_id VARCHAR(128), "
                      "expiration_time DATETIME, "
                      "FOREIGN KEY (router_hash) REFERENCES LeaseSets(hash)"
                      ")");
    
    delete stmt;
}


void MySQLConnector::insertData(int id, const string& name, const string& tablename) {
    sql::PreparedStatement *pstmt;
    pstmt = con_->prepareStatement("INSERT INTO " + tablename +"(id, name) VALUES (?, ?)");
    pstmt->setInt(1, id);
    pstmt->setString(2, name);
    pstmt->execute();
    delete pstmt;
}

// 添加一个 RouterInfo 记录
void MySQLConnector::addRouterInfo(const std::string& hash, bool isFFpeers, const std::string& caps,
                                   const std::string& version, const std::string& netId,
                                   int64_t published, const std::string& cryptoKeyType,
                                   const std::string& signKey, const std::string& NTCP2_ipv4,
                                   int NTCP2_ipv4_port, const std::string& NTCP2_s,
                                   const std::string& NTCP2_i, const std::string& NTCP2_ipv6,
                                   int NTCP2_ipv6_port, const std::string& SSU_ipv4,
                                   int SSU_ipv4_port, const std::string& SSU_ipv6,
                                   int SSU_ipv6_port) {
        
        sql::PreparedStatement *pstmt;
    try {
        pstmt = con_->prepareStatement("INSERT INTO RouterInfo(hash, isFFpeers, caps, version, netId, published_time, updatetime, crytokeytype, signkey, NTCP2_ipv4, NTCP2_ipv4_port, NTCP2_s, NTCP2_i, NTCP2_ipv6, NTCP2_ipv6_port, SSU_ipv4, SSU_ipv4_port, SSU_ipv6, SSU_ipv6_port) "
                                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                                        "ON DUPLICATE KEY UPDATE "
                                        "hash=VALUES(hash), "
                                        "isFFpeers=VALUES(isFFpeers), "
                                        "caps=VALUES(caps), "
                                        "version=VALUES(version), "
                                        "netId=VALUES(netId), "
                                        "published_time=VALUES(published_time), "
                                        "updatetime=VALUES(updatetime), "
                                        "crytokeytype=VALUES(crytokeytype), "
                                        "signkey=VALUES(signkey), "
                                        "NTCP2_ipv4=VALUES(NTCP2_ipv4), "
                                        "NTCP2_ipv4_port=VALUES(NTCP2_ipv4_port), "
                                        "NTCP2_s=VALUES(NTCP2_s), "
                                        "NTCP2_i=VALUES(NTCP2_i), "
                                        "NTCP2_ipv6=VALUES(NTCP2_ipv6), "
                                        "NTCP2_ipv6_port=VALUES(NTCP2_ipv6_port), "
                                        "SSU_ipv4=VALUES(SSU_ipv4), "
                                        "SSU_ipv4_port=VALUES(SSU_ipv4_port), "
                                        "SSU_ipv6=VALUES(SSU_ipv6), "
                                        "SSU_ipv6_port=VALUES(SSU_ipv6_port)");

        time_t timestamp = static_cast<time_t>(published / 1000);
        std::tm* tmInfo = std::localtime(&timestamp);

        pstmt->setString(1, hash);
        pstmt->setBoolean(2, isFFpeers);
        pstmt->setString(3, caps);
        pstmt->setString(4, version);
        pstmt->setString(5, netId);
        pstmt->setDateTime(6, tmToSQLString(tmInfo));
        int64_t currentTimestamp = duration_cast<seconds>(system_clock::now().time_since_epoch()).count();
        time_t nowtime = static_cast<time_t>(currentTimestamp);
        std::tm* nowtmInfo = std::localtime(&nowtime);
        pstmt->setDateTime(7, tmToSQLString(nowtmInfo));
        pstmt->setString(8, cryptoKeyType);
        pstmt->setString(9, signKey);
        pstmt->setString(10, NTCP2_ipv4);
        pstmt->setInt(11, NTCP2_ipv4_port);
        pstmt->setString(12, NTCP2_s);
        pstmt->setString(13, NTCP2_i);
        pstmt->setString(14, NTCP2_ipv6);
        pstmt->setInt(15, NTCP2_ipv6_port);
        pstmt->setString(16, SSU_ipv4);
        pstmt->setInt(17, SSU_ipv4_port);
        pstmt->setString(18, SSU_ipv6);
        pstmt->setInt(19, SSU_ipv6_port);
        pstmt->execute();
        delete pstmt;

    }catch (sql::SQLException& e) {
        // 输出到标准错误流
        std::cerr << "MySQL error (" << e.getErrorCode() << "): " << e.what() << std::endl;

        // 格式化错误信息
        std::ostringstream oss;
        oss << "MySQL error (" << e.getErrorCode() << "): " << e.what();
        std::string errorString = oss.str();

        // 输出到日志文件

        // 连接并创建数据库
        connect();
        createDatabase("darknet");
    }
}

void MySQLConnector::addLeaseSet(const std::string& hash, const std::string& encryption_type,
                                int64_t expiration_time, const std::string& storage_type,
                                const std::string& query_method,
                                const std::vector<std::tuple<std::string, string, uint64_t>>& leases) {
        
        
        sql::PreparedStatement *pstmt;
    try {
        pstmt = con_->prepareStatement("INSERT INTO LeaseSets(hash, encryption_type, expiration_time, storage_type, "
                                        "published_time, updatetime, query_method) "
                                        "VALUES (?, ?, ?, ?, ?, ?, ?) "
                                        "ON DUPLICATE KEY UPDATE "
                                        "hash=VALUES(hash), "
                                        "encryption_type=VALUES(encryption_type), "
                                        "expiration_time=VALUES(expiration_time), "
                                        "storage_type=VALUES(storage_type), "
                                        "published_time=IF(published_time, published_time, VALUES(published_time)), "
                                        "updatetime=VALUES(updatetime), "
                                        "query_method=VALUES(query_method)");

        time_t expirationTimestamp = static_cast<time_t>(expiration_time / 1000);
        std::tm* expirationTmInfo = std::localtime(&expirationTimestamp);


        pstmt->setString(1, hash);
        pstmt->setString(2, encryption_type);
        pstmt->setDateTime(3, tmToSQLString(expirationTmInfo));
        pstmt->setString(4, storage_type);

        int64_t currentTimestamp = duration_cast<seconds>(system_clock::now().time_since_epoch()).count();
        time_t nowtime = static_cast<time_t>(currentTimestamp);
        std::tm* nowtmInfo = std::localtime(&nowtime);
        pstmt->setDateTime(5, tmToSQLString(nowtmInfo));
        pstmt->setDateTime(6, tmToSQLString(nowtmInfo));

        pstmt->setString(7, query_method);
        pstmt->execute();

        delete pstmt;

        // Insert leases into Leases table
        for (const auto& lease : leases) {
            std::string gateway_address = std::get<0>(lease);
            string tunnel_id = std::get<1>(lease);
            uint64_t expiration_time = std::get<2>(lease);
            sql::PreparedStatement *pstmt;
            pstmt = con_->prepareStatement("INSERT INTO Leases(router_hash, gateway_address, tunnel_id, expiration_time) "
                                            "VALUES (?, ?, ?, ?)");
            pstmt->setString(1, hash);
            pstmt->setString(2, gateway_address);
            pstmt->setString(3, tunnel_id);
            time_t expirationTimestamp2 = static_cast<time_t>(expiration_time / 1000);
            std::tm* expirationTmInfo2 = std::localtime(&expirationTimestamp);
            pstmt->setDateTime(4, tmToSQLString(expirationTmInfo2));
            pstmt->execute();
            delete pstmt;
        }
    } catch (sql::SQLException& e) {
        std::cerr << "MySQL error (" << e.getErrorCode() << "): " << e.what() << std::endl;
        std::ostringstream oss;
        oss << "MySQL error (" << e.getErrorCode() << "): " << e.what();
        std::string errorString = oss.str();
        connect();
        createDatabase("darknet");
    }
}


