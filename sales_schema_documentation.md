# Sales Schema Documentation - AdventureWorks Database

This document provides detailed information about all tables in the `sales` schema of the AdventureWorks database. It is designed to help agents understand which tables and columns to use when writing SQL queries to answer business questions.

## Core Transaction Tables

### `customer`
**Purpose**: Stores customer information, linking to either individual persons or business stores.
**Data Nature**: Customer master data with references to persons or stores

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| customerid | integer | NO | Primary key, auto-incrementing customer ID |
| personid | integer | YES | Reference to person.person for individual customers |
| storeid | integer | YES | Reference to sales.store for business customers |
| territoryid | integer | YES | Reference to sales territory |
| rowguid | uuid | NO | Unique identifier for replication |
| modifieddate | timestamp | NO | Record modification timestamp |

**Key Business Use**: Essential for customer analysis, segmentation, and linking orders to customers.

### `salesorderheader`
**Purpose**: Contains header information for sales orders including totals, dates, and customer details.
**Data Nature**: Order-level transactional data with financial totals

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| salesorderid | integer | NO | Primary key, auto-incrementing order ID |
| revisionnumber | smallint | NO | Order revision number (default 0) |
| orderdate | timestamp | NO | Date order was placed (default now()) |
| duedate | timestamp | NO | Date order is due |
| shipdate | timestamp | YES | Date order was shipped |
| status | smallint | NO | Order status code (default 1) |
| onlineorderflag | boolean | NO | Whether order was placed online (default true) |
| purchaseordernumber | varchar(25) | YES | Customer's purchase order number |
| accountnumber | varchar(15) | YES | Customer account number |
| customerid | integer | NO | Foreign key to customer |
| salespersonid | integer | YES | Foreign key to salesperson |
| territoryid | integer | YES | Foreign key to territory |
| billtoaddressid | integer | NO | Billing address reference |
| shiptoaddressid | integer | NO | Shipping address reference |
| shipmethodid | integer | NO | Shipping method reference |
| creditcardid | integer | YES | Credit card used for payment |
| creditcardapprovalcode | varchar(15) | YES | Credit card approval code |
| currencyrateid | integer | YES | Currency conversion rate |
| subtotal | numeric | NO | Order subtotal (default 0.00) |
| taxamt | numeric | NO | Tax amount (default 0.00) |
| freight | numeric | NO | Freight charges (default 0.00) |
| totaldue | numeric | YES | Total amount due |
| comment | varchar(128) | YES | Order comments |
| rowguid | uuid | NO | Unique identifier for replication |
| modifieddate | timestamp | NO | Record modification timestamp |

**Key Business Use**: Central table for order analysis, revenue reporting, sales performance, and customer behavior analysis.

### `salesorderdetail`
**Purpose**: Contains line item details for sales orders including products, quantities, and pricing.
**Data Nature**: Line-item transactional data for detailed product sales analysis

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| salesorderid | integer | NO | Foreign key to salesorderheader |
| salesorderdetailid | integer | NO | Primary key, auto-incrementing detail ID |
| carriertrackingnumber | varchar(25) | YES | Carrier tracking number |
| orderqty | smallint | NO | Quantity ordered |
| productid | integer | NO | Foreign key to product |
| specialofferid | integer | NO | Foreign key to special offer |
| unitprice | numeric | NO | Unit price of product |
| unitpricediscount | numeric | NO | Discount per unit (default 0.0) |
| rowguid | uuid | NO | Unique identifier for replication |
| modifieddate | timestamp | NO | Record modification timestamp |

**Key Business Use**: Essential for product analysis, pricing analysis, discount effectiveness, and detailed sales reporting.

## People and Organizations

### `salesperson`
**Purpose**: Stores salesperson information including quotas and performance metrics.
**Data Nature**: Employee master data with sales performance tracking

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| businessentityid | integer | NO | Primary key, reference to person |
| territoryid | integer | YES | Assigned territory |
| salesquota | numeric | YES | Sales quota target |
| bonus | numeric | NO | Bonus amount (default 0.00) |
| commissionpct | numeric | NO | Commission percentage (default 0.00) |
| salesytd | numeric | NO | Sales year-to-date (default 0.00) |
| saleslastyear | numeric | NO | Sales last year (default 0.00) |
| rowguid | uuid | NO | Unique identifier for replication |
| modifieddate | timestamp | NO | Record modification timestamp |

**Key Business Use**: Salesperson performance analysis, quota tracking, commission calculations, and territory management.

### `store`
**Purpose**: Stores information about business customers (retail stores).
**Data Nature**: Business customer master data with demographics

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| businessentityid | integer | NO | Primary key, reference to business entity |
| name | varchar(50) | NO | Store name |
| salespersonid | integer | YES | Assigned salesperson |
| demographics | xml | YES | Store demographic data in XML format |
| rowguid | uuid | NO | Unique identifier for replication |
| modifieddate | timestamp | NO | Record modification timestamp |

**Key Business Use**: B2B customer analysis, store demographics analysis, and salesperson-store relationships.

## Territory and Geographic Data

### `salesterritory`
**Purpose**: Defines sales territories with performance metrics.
**Data Nature**: Geographic/organizational sales regions with performance tracking

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| territoryid | integer | NO | Primary key, auto-incrementing territory ID |
| name | varchar(50) | NO | Territory name (e.g., "Northwest", "Northeast") |
| countryregioncode | varchar(3) | NO | Country/region code |
| group | varchar(50) | NO | Territory group (e.g., "North America") |
| salesytd | numeric | NO | Territory sales year-to-date (default 0.00) |
| saleslastyear | numeric | NO | Territory sales last year (default 0.00) |
| costytd | numeric | NO | Territory cost year-to-date (default 0.00) |
| costlastyear | numeric | NO | Territory cost last year (default 0.00) |
| rowguid | uuid | NO | Unique identifier for replication |
| modifieddate | timestamp | NO | Record modification timestamp |

**Key Business Use**: Geographic sales analysis, territory performance comparison, regional revenue reporting.

### `salesterritoryhistory`
**Purpose**: Tracks historical assignments of salespeople to territories.
**Data Nature**: Historical tracking data for territory assignments

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| businessentityid | integer | NO | Salesperson ID |
| territoryid | integer | NO | Territory ID |
| startdate | timestamp | NO | Assignment start date |
| enddate | timestamp | YES | Assignment end date (NULL if current) |
| rowguid | uuid | NO | Unique identifier for replication |
| modifieddate | timestamp | NO | Record modification timestamp |

**Key Business Use**: Historical territory analysis, salesperson mobility tracking, territory coverage analysis.

## Promotions and Pricing

### `specialoffer`
**Purpose**: Stores promotional offers and discount campaigns.
**Data Nature**: Marketing campaign data with discount terms and validity periods

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| specialofferid | integer | NO | Primary key, auto-incrementing offer ID |
| description | varchar(255) | NO | Offer description |
| discountpct | numeric | NO | Discount percentage (default 0.00) |
| type | varchar(50) | NO | Offer type |
| category | varchar(50) | NO | Offer category |
| startdate | timestamp | NO | Offer start date |
| enddate | timestamp | NO | Offer end date |
| minqty | integer | NO | Minimum quantity required (default 0) |
| maxqty | integer | YES | Maximum quantity allowed |
| rowguid | uuid | NO | Unique identifier for replication |
| modifieddate | timestamp | NO | Record modification timestamp |

**Key Business Use**: Promotion effectiveness analysis, discount impact on sales, campaign performance tracking.

### `specialofferproduct`
**Purpose**: Links special offers to specific products (many-to-many relationship).
**Data Nature**: Product-offer association data

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| specialofferid | integer | NO | Foreign key to specialoffer |
| productid | integer | NO | Foreign key to product |
| rowguid | uuid | NO | Unique identifier for replication |
| modifieddate | timestamp | NO | Record modification timestamp |

**Key Business Use**: Determining which products are included in promotions, analyzing promotional product performance.

## Financial and Currency

### `currency`
**Purpose**: Master list of currencies supported by the system.
**Data Nature**: Reference data for currency codes and names

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| currencycode | char(3) | NO | Primary key, ISO currency code |
| name | varchar(50) | NO | Currency name |
| modifieddate | timestamp | NO | Record modification timestamp |

**Key Business Use**: Multi-currency reporting, currency reference for international sales.

### `currencyrate`
**Purpose**: Stores currency exchange rates for different dates.
**Data Nature**: Time-series financial data for currency conversions

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| currencyrateid | integer | NO | Primary key, auto-incrementing rate ID |
| currencyratedate | timestamp | NO | Date of exchange rate |
| fromcurrencycode | char(3) | NO | Source currency code |
| tocurrencycode | char(3) | NO | Target currency code |
| averagerate | numeric | NO | Average exchange rate |
| endofdayrate | numeric | NO | End of day exchange rate |
| modifieddate | timestamp | NO | Record modification timestamp |

**Key Business Use**: Currency conversion for international sales analysis, historical exchange rate analysis.

### `countryregioncurrency`
**Purpose**: Associates countries/regions with their currencies.
**Data Nature**: Geographic-currency reference data

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| countryregioncode | varchar(3) | NO | Country/region code |
| currencycode | char(3) | NO | Currency code used in this region |
| modifieddate | timestamp | NO | Record modification timestamp |

**Key Business Use**: Geographic currency analysis, regional financial reporting.

### `creditcard`
**Purpose**: Stores credit card information (masked/encrypted).
**Data Nature**: Payment method reference data

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| creditcardid | integer | NO | Primary key, auto-incrementing card ID |
| cardtype | varchar(50) | NO | Credit card type (Visa, MasterCard, etc.) |
| cardnumber | varchar(25) | NO | Masked/encrypted card number |
| expmonth | smallint | NO | Expiration month |
| expyear | smallint | NO | Expiration year |
| modifieddate | timestamp | NO | Record modification timestamp |

**Key Business Use**: Payment method analysis, credit card type preferences.

### `personcreditcard`
**Purpose**: Links individuals to their credit cards.
**Data Nature**: Person-payment method association

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| businessentityid | integer | NO | Person ID |
| creditcardid | integer | NO | Credit card ID |
| modifieddate | timestamp | NO | Record modification timestamp |

**Key Business Use**: Customer payment method analysis, credit card usage patterns.

## Tax and Compliance

### `salestaxrate`
**Purpose**: Stores tax rates for different states/provinces and tax types.
**Data Nature**: Tax compliance reference data

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| salestaxrateid | integer | NO | Primary key, auto-incrementing tax rate ID |
| stateprovinceid | integer | NO | State/province identifier |
| taxtype | smallint | NO | Type of tax |
| taxrate | numeric | NO | Tax rate percentage (default 0.00) |
| name | varchar(50) | NO | Tax rate name |
| rowguid | uuid | NO | Unique identifier for replication |
| modifieddate | timestamp | NO | Record modification timestamp |

**Key Business Use**: Tax calculation, compliance reporting, geographic tax analysis.

## Sales Analytics and Reasons

### `salesreason`
**Purpose**: Catalog of reasons why customers make purchases.
**Data Nature**: Marketing/sales analysis reference data

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| salesreasonid | integer | NO | Primary key, auto-incrementing reason ID |
| name | varchar(50) | NO | Reason name (e.g., "Price", "On Promotion") |
| reasontype | varchar(50) | NO | Category of reason (e.g., "Marketing", "Promotion") |
| modifieddate | timestamp | NO | Record modification timestamp |

**Example Values**: "Price", "On Promotion", "Magazine Advertisement", "Television Advertisement"

**Key Business Use**: Sales motivation analysis, marketing effectiveness tracking.

### `salesorderheadersalesreason`
**Purpose**: Links sales orders to the reasons customers purchased (many-to-many).
**Data Nature**: Order-reason association data

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| salesorderid | integer | NO | Foreign key to salesorderheader |
| salesreasonid | integer | NO | Foreign key to salesreason |
| modifieddate | timestamp | NO | Record modification timestamp |

**Key Business Use**: Analyzing what motivates customer purchases, marketing campaign effectiveness.

## Performance Tracking

### `salespersonquotahistory`
**Purpose**: Historical record of salesperson quota changes over time.
**Data Nature**: Historical performance tracking data

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| businessentityid | integer | NO | Salesperson ID |
| quotadate | timestamp | NO | Date quota was set |
| salesquota | numeric | NO | Quota amount |
| rowguid | uuid | NO | Unique identifier for replication |
| modifieddate | timestamp | NO | Record modification timestamp |

**Key Business Use**: Quota trend analysis, performance target tracking, compensation analysis.

## E-commerce

### `shoppingcartitem`
**Purpose**: Stores items in customer shopping carts (for online orders).
**Data Nature**: E-commerce session data for cart abandonment analysis

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| shoppingcartitemid | integer | NO | Primary key, auto-incrementing item ID |
| shoppingcartid | varchar(50) | NO | Shopping cart session ID |
| quantity | integer | NO | Quantity in cart (default 1) |
| productid | integer | NO | Product in cart |
| datecreated | timestamp | NO | When item was added to cart |
| modifieddate | timestamp | NO | Record modification timestamp |

**Key Business Use**: Cart abandonment analysis, online shopping behavior, conversion rate optimization.

## Views (Read-Only Aggregated Data)

The schema also includes several views that provide pre-aggregated or formatted data:

### `vindividualcustomer`
**Purpose**: Individual customers with formatted contact information.

### `vpersondemographics`
**Purpose**: Person demographic information in structured format.

### `vsalesperson`
**Purpose**: Salesperson information with additional computed fields.

### `vsalespersonsalesbyfiscalyears`
**Purpose**: Salesperson sales aggregated by fiscal year.

### `vsalespersonsalesbyfiscalyearsdata`
**Purpose**: Supporting data for fiscal year sales analysis.

### `vstorewithaddresses`
**Purpose**: Store information combined with address details.

### `vstorewithcontacts`
**Purpose**: Store information combined with contact details.

### `vstorewithdemographics`
**Purpose**: Store information with parsed demographic data.

## Common Query Patterns

### Revenue Analysis
- Use `salesorderheader` for order-level revenue
- Join with `salesorderdetail` for product-level analysis
- Filter by `orderdate` for time-period analysis

### Customer Analysis
- Start with `customer` table
- Join with `salesorderheader` for purchase history
- Use `salesterritory` for geographic segmentation

### Product Performance
- Use `salesorderdetail` for detailed product sales
- Join with `specialofferproduct` and `specialoffer` for promotion analysis
- Group by `productid` for product rankings

### Salesperson Performance
- Use `salesperson` for current performance metrics
- Join with `salesorderheader` via `salespersonid` for detailed analysis
- Use `salespersonquotahistory` for historical quota analysis

### Geographic Analysis
- Use `salesterritory` for regional performance
- Join customers and orders via `territoryid`
- Combine with `countryregioncurrency` for international analysis

This documentation provides the foundation for understanding the AdventureWorks sales schema and writing effective SQL queries for business analysis.