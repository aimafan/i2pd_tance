#ifndef MYSQL_CONNECTOR_H
#define MYSQL_CONNECTOR_H

#include <mysql_driver.h>
#include <mysql_connection.h>
#include <cppconn/statement.h>
#include <cppconn/prepared_statement.h>
#include <cppconn/resultset.h>
#include <cppconn/exception.h>
#include <iomanip>
#include <chrono>
#include <string>
#include "Logger.h"

using namespace std;
using namespace chrono;

class MySQLConnector {
public:
    MySQLConnector(const string& host, const string& user, const string& password);
    ~MySQLConnector();

    void connect();
    void createDatabase(const string& dbName);
    void createRouterinfoTable();
    void createLeaseSetsTable();
    void insertData(int id, const string& name, const string& tablename);
    void addRouterInfo(const std::string& hash, bool isFFpeers, const std::string& caps,
                                   const std::string& version, const std::string& netId,
                                   int64_t published, const std::string& cryptoKeyType,
                                   const std::string& signKey, const std::string& NTCP2_ipv4,
                                   int NTCP2_ipv4_port, const std::string& NTCP2_s,
                                   const std::string& NTCP2_i, const std::string& NTCP2_ipv6,
                                   int NTCP2_ipv6_port, const std::string& SSU_ipv4,
                                   int SSU_ipv4_port, const std::string& SSU_ipv6,
                                   int SSU_ipv6_port);
    void addLeaseSet(const std::string& hash, const std::string& encryption_type,
                                int64_t expiration_time, const std::string& storage_type,
                                const std::string& query_method,
                                const std::vector<std::tuple<std::string, string, uint64_t>>& leases);
    void createKeyTable();

private:
    sql::mysql::MySQL_Driver *driver_;
    sql::Connection *con_;
    string host_;
    string user_;
    string password_;
};

#endif // MYSQL_CONNECTOR_H