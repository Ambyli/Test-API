from enum import Enum


class Endpoints(Enum):
    # endpoint names
    ACTIVEFIXITS_GET = 1
    ACTIVESTOCKTYPES_GET = 2
    ALIGNERBATCHES_POST = 3
    ALIGNERBATCHES_LOCATION_GET = 4
    ALIGNERFILELINKS_GET = 5
    ALIGNERFILELINKS_POST = 6
    ALIGNERFILELINKS_DELETE = 7
    ALIGNERFILELINKSMATCHER_POST = 8
    ALIGNERFILELINKS_ALIGNER_GET = 9
    ALIGNERFILELINKS_ALIGNER_POST = 10
    ALIGNERFILELINKS_ID_GET = 11
    ALIGNERFILELINKS_ID_PUT = 12
    ALIGNERFILENAME_GET = 13
    ALIGNERLOCATIONLOOKBACK_POST = 14
    ALIGNERLOGS_ALIGNER_GET = 15
    ALIGNERLOGS_ALIGNER_POST = 16
    ALIGNERLOTLINKS_GET = 17
    ALIGNERLOTLINKS_POST = 18
    ALIGNERLOTLINKS_ALIGNER_GET = 19
    ALIGNERLOTLINKS_ID_GET = 20
    ALIGNERLOTLINKS_ID_PUT = 21
    ALIGNERLOTLINKS_ID_DELETE = 22
    ALIGNERLOTLINKS_LOT_GET = 23
    ALIGNERQTY_GET = 24
    ALIGNERQTY_PRODUCTIONLINES_GET = 25
    ALIGNERS_GET = 26
    ALIGNERS_POST = 27
    ALIGNERS_PUT = 28
    ALIGNERS_ALIGNER_GET = 29
    ALIGNERS_ALIGNER_POST = 30
    ALIGNERS_ALIGNER_PUT = 31
    ALIGNERS_BAG_GET = 32
    ALIGNERS_BAG_POST = 33
    ALIGNERS_BATCH_GET = 34
    ALIGNERS_BATCH_POST = 35
    ALIGNERS_CASE_GET = 36
    ALIGNERS_CASE_PUT = 37
    ALIGNERS_CASE_POST = 38
    ALIGNERS_FIXIT_CID_GET = 39
    ALIGNERS_FIXIT_ID_GET = 40
    ALIGNERS_LOCATION_GET = 41
    ALIGNERS_LOCATIONS_GET = 42
    ALIGNERS_LOT_GET = 43
    ALIGNERS_PLASTICLOTNUMBER_GET = 44
    ALIGNERS_REMAKE_GET = 45
    ALIGNERS_REMAKE_POST = 46
    BAGGING_GET = 47
    BAGGING_POST = 48
    BAGGING_ALIGNER_GET = 49
    BAGLINKS_ALIGNER_GET = 50
    BAGRECORDLOGS_CASE_GET = 51
    BAGRECORDS_GET = 52
    BAGRECORDS_POST = 53
    BAGRECORDS_BAG_GET = 54
    BAGRECORDS_BAG_PUT = 55
    BAGRECORDS_BAG_DELETE = 56
    BAGRECORDS_CASE_GET = 57
    BAGRECORDS_CASE_DELETE = 58
    BAGS_GET = 59
    BAGS_POST = 60
    BAGS_ALIGNER_PUT = 61
    BAGS_ALIGNERS_POST = 62
    BAGS_LINK_GET = 63
    BINS_GET = 64
    BINS_POST = 65
    BINS_BIN_GET = 66
    BINS_BIN_PUT = 67
    BULLETINFILELINKS_GET = 68
    BULLETINFILELINKS_POST = 69
    BULLETINFILELINKS_BULLETIN_GET = 70
    BULLETINFILELINKS_LINK_GET = 71
    BULLETINFILELINKS_LINK_PUT = 72
    BULLETINS_GET = 73
    BULLETINS_POST = 74
    BULLETINS_BULLETIN_GET = 75
    BULLETINS_BULLETIN_PUT = 76
    BULLETINS_BULLETIN_DELETE = 77
    BULLETINS_FILTER_GET = 78
    BULLETINS_FILTER_POST = 79
    BULLETINTAGLINKS_GET = 80
    BULLETINTAGLINKS_POST = 81
    BULLETINTAGLINKS_BULLETIN_GET = 82
    BULLETINTAGLINKS_LINK_GET = 83
    BULLETINTAGLINKS_LINK_PUT = 84
    CARBONPLATELOGS_GET = 85
    CARBONPLATELOGS_POST = 86
    CARBONPRINTER_ATTACHMENTS_GET = 87
    CARBONPRINTER_BUILDS_GET = 88
    CARBONPRINTER_PARTS_GET = 89
    CARBONPRINTER_PLATE_GET = 90
    CARBONPRINTER_PRINTEDPARTS_GET = 91
    CARBONPRINTER_PRINTEDPARTS_POST = 92
    CARBONPRINTER_PRINTERS_GET = 93
    CARBONPRINTER_PRINTS_GET = 94
    CARBONPRINTER_PRINTS_POST = 95
    CARBONPRINTER_QUEUES_GET = 96
    CARBONS_GET = 97
    CARBONS_POST = 98
    CARBONS_PUT = 99
    CARBONS_ALIGNER_GET = 100
    CARBONS_CASE_GET = 101
    CARBONS_FILENAME_GET = 102
    CASEEMPLOYEELINKLOGS_GET = 103
    CASEEMPLOYEELINKLOGS_EMPLOYEE_GET = 104
    CASEEMPLOYEELINKS_GET = 105
    CASEEMPLOYEELINKS_POST = 106
    CASEEMPLOYEELINKS_PUT = 107
    CASEEMPLOYEELINKS_CASE_GET = 108
    CASEEMPLOYEELINKS_CASE_POST = 109
    CASEFILELINKS_CASE_GET = 110
    CASEFILELINKS_CASE_POST = 111
    CASEFILELINKS_LINK_DELETE = 112
    CASEFILTERS_GET = 113
    CASEFLAGLINKLOGS_CASE_GET = 114
    CASEFLAGLINKS_GET = 115
    CASEFLAGLINKS_POST = 116
    CASEFLAGLINKS_PUT = 117
    CASEFLAGS_GET = 118
    CASEFLAGS_POST = 119
    CASEFLAGS_PUT = 120
    CASEFLAGS_CASE_GET = 121
    CASEREPORTLINKS_GET = 122
    CASEREPORTLINKS_POST = 123
    CASEREPORTLINKS_PUT = 124
    CASEREPORTLINKS_CASE_GET = 125
    CASES_GET = 126
    CASES_POST = 127
    CASESPENDING_LOCATION_GET = 128
    CASES_CASE_GET = 129
    CASES_FILTER_POST = 130
    CASES_FIXIT_GET = 131
    CASES_ID_GET = 132
    CASES_PRODUCTIONLINE_GET = 133
    CASES_PRODUCTIONLINE_POST = 134
    CHARTDASHBOARDLINKS_GET = 135
    CHARTDASHBOARDLINKS_POST = 136
    CHARTDASHBOARDLINKS_PUT = 137
    CHARTDASHBOARDLINKS_DELETE = 138
    CHARTS_GET = 139
    CHARTS_POST = 140
    CHARTS_CHART_GET = 141
    CHARTS_CHART_PUT = 142
    CHARTS_CHART_DELETE = 143
    CHARTS_DASHBOARD_GET = 144
    CHARTS_EMPLOYEE_GET = 145
    CHARTS_QUERY_GET = 146
    CHARTS_TYPE_GET = 147
    CHARTTYPES_GET = 148
    CUSTOMERACCOUNTS_CUSTOMER_GET = 149
    CUSTOMERACCOUNTS_CUSTOMER_POST = 150
    CUSTOMERCATALOGS_CUSTOMER_GET = 151
    CUSTOMERS_GET = 152
    CUSTOMERS_POST = 436
    CUSTOMERS_CUSTOMER_GET = 153
    DASHBOARDS_GET = 154
    DASHBOARDS_POST = 155
    DASHBOARDS_CHART_GET = 156
    DASHBOARDS_DASHBOARD_GET = 157
    DASHBOARDS_DASHBOARD_PUT = 158
    DASHBOARDS_DASHBOARD_DELETE = 159
    DASHBOARDS_EMPLOYEE_GET = 160
    DUPLICATECASES_GET = 161
    EMPLOYEEASSETLINKS_GET = 162
    EMPLOYEEASSETLINKS_POST = 163
    EMPLOYEEASSETLINKS_PUT = 164
    EMPLOYEEASSETLINKS_EMPLOYEE_GET = 165
    EMPLOYEECHECK_POST = 166
    EMPLOYEELOCATIONLINKS_GET = 167
    EMPLOYEELOCATIONLINKS_POST = 168
    EMPLOYEELOCATIONLINKS_PUT = 169
    EMPLOYEELOCATIONLINKS_EMPLOYEE_GET = 170
    EMPLOYEELOCATIONLINKS_LOCATION_GET = 171
    EMPLOYEEPUNCHLINKS_GET = 172
    EMPLOYEEPUNCHLINKS_POST = 173
    EMPLOYEEPUNCHLINKS_PUT = 174
    EMPLOYEES_GET = 175
    EMPLOYEES_POST = 176
    EMPLOYEESTATS_GET = 177
    EMPLOYEESTATS_LOCATION_GET = 178
    EMPLOYEES_EMPLOYEE_GET = 179
    EMPLOYEES_EMPLOYEE_PUT = 180
    EMPLOYEES_TEAM_GET = 181
    EMPLOYEETEAMS_GET = 182
    EMPLOYEETOKENLINKS_GET = 183
    EMPLOYEETOKENLINKS_POST = 184
    ENDPOINTPARAMLINKS_GET = 185
    ENDPOINTPARAMLINKS_POST = 186
    ENDPOINTPARAMLINKS_PUT = 187
    ENDPOINTPARAMLINKS_DELETE = 188
    ENDPOINTPARAMS_ENDPOINT_GET = 189
    ENDPOINTS_GET = 190
    ENDPOINTS_POST = 191
    ENDPOINTS_EMPLOYEE_GET = 192
    ENDPOINTS_ENDPOINT_GET = 193
    ENDPOINTS_ENDPOINT_PUT = 194
    ENDPOINTS_ENDPOINT_DELETE = 195
    ENDPOINTS_TOKEN_GET = 196
    ENDPOINTTOKENCHECKS_ENDPOINT_PUT = 197
    FILES_GET = 198
    FILES_POST = 199
    FILES_BATCH_GET = 200
    FILES_BULLETIN_GET = 201
    FILES_FILE_GET = 202
    FILES_FILE_POST = 203
    FILES_TYPE_POST = 204
    FILETYPES_GET = 205
    FIXITEMPLOYEELINKLOGS_GET = 206
    FIXITEMPLOYEELINKLOGS_EMPLOYEE_GET = 207
    FIXITEMPLOYEELINKS_GET = 208
    FIXITEMPLOYEELINKS_POST = 209
    FIXITEMPLOYEELINKS_PUT = 210
    FIXITEMPLOYEELINKS_FIXIT_GET = 211
    FIXITEMPLOYEELINKS_FIXIT_POST = 212
    FIXITREASONS_GET = 213
    FIXITS_GET = 214
    FIXITS_POST = 215
    FIXITS_PUT = 216
    FIXITS_ALIGNER_POST = 217
    FIXITS_CASE_GET = 218
    FIXITS_FIXIT_GET = 219
    FIXITS_FIXIT_PUT = 220
    FIXITS_LOCATION_GET = 221
    FIXITS_REASON_GET = 222
    FIXITS_WHO_GET = 223
    GAUGES_GET = 224
    GAUGES_POST = 225
    GAUGES_PUT = 226
    HEALTH_GET = 227
    IOTSENSORS_GET = 228
    IOTSENSORS_POST = 229
    KEYENCELASERPROFILE_GET = 230
    KEYENCELASERPROFILE_POST = 231
    LASERRECORDLOGS_CASE_GET = 232
    LASERRECORDS_GET = 233
    LASERRECORDS_POST = 234
    LASERRECORDS_CASE_GET = 235
    LASERRECORDS_CASE_DELETE = 236
    LASERRECORDS_LASER_GET = 237
    LASERRECORDS_LASER_PUT = 238
    LASERRECORDS_LASER_DELETE = 239
    LINES_GET = 240
    LINES_POST = 241
    LINES_LINE_GET = 242
    LINES_LINE_PUT = 243
    LINES_LINE_DELETE = 244
    LINES_OWNER_GET = 245
    LOCATIONGOALS_GET = 246
    LOCATIONGOALS_LOCATION_GET = 247
    LOCATIONS_GET = 248
    LOCATIONSFOLLOWING_LOCATION_GET = 249
    LOCATIONSPREVIOUS_LOCATION_GET = 250
    LOCATIONS_STATUS_GET = 251
    LOCATIONS_STOCK_GET = 252
    LOCATIONS_STOCKSTORAGE_PUT = 253
    LOCKS_GET = 254
    LOCKS_LOCK_GET = 255
    LOCKS_LOCK_POST = 256
    LOCKS_LOCK_PUT = 257
    LOCKS_LOCK_STATUS_POST = 258
    LOGIN_POST = 259
    LOGTYPES_GET = 260
    LOTS_GET = 261
    LOTS_POST = 262
    LOTS_PUT = 263
    LOTS_BIN_GET = 264
    LOTS_LOT_GET = 265
    LOTS_LOT_BIN_PUT = 266
    LOTS_LOT_STATUS_PUT = 267
    LOTS_LOT_YIELD_PUT = 268
    LOTS_PRODUCTIONLINE_GET = 269
    LOTS_PRODUCTIONLINE_PUT = 270
    LOTS_YIELD_GET = 271
    MATERIALS_GET = 272
    MATERIALS_POST = 273
    OWNEREMPLOYEELINKS_POST = 274
    OWNEREMPLOYEELINKS_LINK_DELETE = 275
    OWNEREMPLOYEELINKS_OWNER_GET = 276
    OWNERLINELINKS_POST = 277
    OWNERLINELINKS_DELETE = 278
    OWNERS_GET = 279
    PARAMS_GET = 280
    PARAMS_POST = 281
    PARAMS_PARAM_PUT = 282
    PATHCONVERT_POST = 283
    PERMISSIONS_GET = 284
    PERMISSIONS_ROLE_GET = 285
    PLASTICMATERIALS_GET = 286
    PLASTICS_GET = 287
    PLASTICS_POST = 288
    PLASTICS_PUT = 289
    PLASTICS_BATCH_GET = 290
    PLASTICS_PLASTIC_GET = 291
    PLASTICS_PLASTIC_PUT = 292
    PLASTICS_PLASTIC_AMOUNT_PUT = 293
    PLASTICS_PLASTIC_BAKE_PUT = 294
    PLASTICS_PLASTIC_STATUS_PUT = 295
    PRODUCTIONLINES_GET = 296
    PRODUCTKITFILELINKS_GET = 297
    PRODUCTKITFILELINKS_POST = 298
    PRODUCTKITFILELINKS_DELETE = 299
    PRODUCTKITS_GET = 300
    PRODUCTKITS_POST = 301
    PRODUCTKITS_DELETE = 302
    PRODUCTS_GET = 437
    PRODUCTS_ALIGNER_GET = 303
    PRODUCTS_ALIGNER_PUT = 304
    PRODUCTS_CASE_GET = 305
    PRODUCTS_CATALOG_GET = 306
    PRODUCTS_PRODUCT_GET = 307
    PRODUCTTYPES_GET = 308
    QUERIES_GET = 309
    QUERIES_POST = 310
    QUERIES_QUERY_GET = 311
    QUERIES_QUERY_PUT = 312
    QUERIES_QUERY_DELETE = 313
    QUERIES_REPORT_GET = 314
    QUERYEXECUTE_POST = 315
    REPAIRYIELDS_GET = 316
    REPAIRYIELDS_POST = 317
    REPORTQUERYLINKS_GET = 318
    REPORTQUERYLINKS_POST = 319
    REPORTQUERYLINKS_PUT = 320
    REPORTQUERYLINKVARIABLES_GET = 321
    REPORTQUERYLINKVARIABLES_POST = 322
    REPORTQUERYLINKVARIABLES_PUT = 323
    REPORTQUERYLINKVARIABLES_DELETE = 324
    REPORTS_GET = 325
    REPORTS_POST = 326
    REPORTS_PUT = 327
    REPORTS_DELETE = 328
    REPORTS_REPORT_GET = 329
    ROLEPERMISSIONLINKS_GET = 330
    ROLEPERMISSIONLINKS_POST = 331
    ROLEPERMISSIONLINKS_PUT = 332
    ROLES_GET = 333
    ROLES_POST = 334
    ROLES_PUT = 335
    ROLES_DELETE = 336
    SAGS_PLASTIC_GET = 337
    SAGS_PLASTIC_POST = 338
    SAGS_YIELD_GET = 339
    SAGS_YIELD_POST = 340
    SEVERITYTYPES_GET = 341
    SHADE_CONSTRUCT_POST = 342
    SHADE_DECONSTRUCT_POST = 343
    SHIPPINGRECORDLOGS_CASE_GET = 344
    SHIPPINGRECORDS_GET = 345
    SHIPPINGRECORDS_POST = 346
    SHIPPINGRECORDS_CASE_GET = 347
    SHIPPINGRECORDS_CASE_DELETE = 348
    SHIPPINGRECORDS_SHIPPING_GET = 349
    SHIPPINGRECORDS_SHIPPING_PUT = 350
    SHIPPINGRECORDS_SHIPPING_DELETE = 351
    STATIONS_GET = 352
    STATIONS_POST = 353
    STATIONS_DELETE = 354
    STATIONS_ALIGNER_GET = 355
    STATIONS_ALIGNER_LOCATION_POST = 356
    STATUSTYPES_GET = 357
    STEPFILEMATCHER_POST = 358
    STOCKACTIONS_GET = 359
    STOCKACTIONS_POST = 360
    STOCKACTIONS_PUT = 361
    STOCKACTIONS_ACTION_GET = 362
    STOCKACTIONS_ACTION_PUT = 363
    STOCKACTIONS_BARCODE_GET = 364
    STOCKACTIONS_LOCATION_GET = 365
    STOCKLINKS_ACTION_GET = 366
    STOCKLINKS_ACTION_POST = 367
    STOCKLINKS_ACTION_PUT = 368
    STOCKLINKS_ACTION_DELETE = 369
    STOCKLINKS_ACTIONBARCODE_GET = 370
    STOCKLINKS_ACTION_BULK_POST = 371
    STOCKS_GET = 372
    STOCKSTORAGE_GET = 373
    STOCKSTORAGE_POST = 374
    STOCKSTORAGE_PUT = 375
    STOCKSTORAGEBATCHFILE_BATCH_GET = 376
    STOCKSTORAGEBATCHHISTORY_LOCATION_GET = 377
    STOCKSTORAGEBATCH_BATCH_GET = 378
    STOCKSTORAGEBATCH_FILELINKS_POST = 379
    STOCKSTORAGEBATCH_LOCATION_GET = 380
    STOCKSTORAGECHECK_POST = 381
    STOCKSTORAGELOGS_LOCATION_GET = 382
    STOCKSTORAGELOGS_STOCK_GET = 383
    STOCKSTORAGE_BATCH_GET = 384
    STOCKSTORAGE_LOCATION_GET = 385
    STOCKSTORAGE_LOCATION_STATUS_GET = 386
    STOCKSTORAGE_STOCK_PUT = 387
    STOCKSTORAGE_STOCK_LOCATION_GET = 388
    STOCKTYPELOG_STOCK_GET = 389
    STOCKTYPES_GET = 390
    STOCKTYPES_POST = 391
    STOCKTYPES_PUT = 392
    STOCKTYPES_ID_GET = 393
    STOCKTYPES_ID_PUT = 394
    TAGS_GET = 395
    TAGS_POST = 396
    TAGS_TAG_GET = 397
    TAGS_TAG_PUT = 398
    TAGS_TAG_DELETE = 399
    THERMOS_GET = 400
    THERMOS_POST = 401
    TIMER_GET = 402
    TOKENENDPOINTLINKS_GET = 403
    TOKENENDPOINTLINKS_POST = 404
    TOKENENDPOINTLINKS_DELETE = 405
    TOKENENDPOINTPARAMLINKS_POST = 406
    TOKENENDPOINTPARAMLINKS_PUT = 407
    TOKENENDPOINTPARAMLINKS_TOKEN_GET = 408
    TOKENENDPOINTPARAMLINKS_TOKEN_DELETE = 409
    TOKENS_GET = 410
    TOKENS_POST = 411
    TOKENS_OWNERS_GET = 412
    TOKENS_TOKEN_PUT = 413
    TOKENS_TOKEN_DELETE = 414
    USERS_GET = 415
    USERS_POST = 416
    USERS_PUT = 417
    USERS_DELETE = 418
    USERS_ACCOUNT_GET = 419
    USERS_EMPLOYEE_GET = 420
    USERS_PASSWORD_PUT = 421
    USERS_PASSWORD_PATCH = 422
    VENDORS_GET = 423
    VENDORS_POST = 424
    YIELDS_GET = 425
    YIELDS_POST = 426
    YIELDS_PUT = 427
    YIELDS_LOT_GET = 428
    YIELDS_PLASTIC_GET = 429
    YIELDS_YIELD_GET = 430
    YIELDS_YIELD_PUT = 431
    YIELDS_YIELD_QUANTITY_GET = 432
    YIELDS_YIELD_QUANTITY_PUT = 433
    ZPL_POST = 434
    STOCKTYPELOG_GET = 435
    ALIGNERLOCATIONS_ALIGNER_PUT = 438
    FILES_BLOB_GET = 439
    FILES_BLOB_POST = 440
    CASELOCATIONS_CASE_PUT = 441
    FIXITLOCATIONS_FIXIT_PUT = 442
    STOCKSTORAGE_STATUS_BULK_PUT = 443
    WASTETYPES_GET = 444
    WASTETYPES_POST = 445
    WASTETYPES_WASTETYPE_PUT = 446
    WASTERECORDS_GET = 447
    WASTERECORDS_POST = 448
    WASTERECORDS_WASTERECORD_PUT = 449
    WASTERECORDS_WASTERECORD_DELETE = 450
    WASTERECORDS_WASTERECORD_GET = 451
    DEPARTMENTS_GET = 452
    ALIGNERS_DUPLICATE_POST = 453
    TOKENENDPOINTPARAMLINKS_TOKEN_PUT = 454
    TOKENENDPOINTPARAMLINKS_STATUS_PUT = 456
    CASES_REMAKE_POST = 457
    CASES_INVOICE_POST = 458
    CASES_INVOICE_DELETE = 459
    EMPLOYEENOTIFICATIONAUTOMATIONLINKS_GET = 460
    EMPLOYEENOTIFICATIONAUTOMATIONLINKS_POST = 461
    EMPLOYEENOTIFICATIONAUTOMATIONLINKS_LINK_PUT = 462
    EMPLOYEES_NOTIFICATIONAUTOMATION_GET = 463
    NOTIFICATIONAUTOMATIONLOGS_GET = 464
    NOTIFICATIONAUTOMATIONLOGS_POST = 465
    NOTIFICATIONAUTOMATIONMESSAGELINKS_GET = 466
    NOTIFICATIONAUTOMATIONMESSAGELINKS_POST = 467
    NOTIFICATIONAUTOMATIONMESSAGELINKS_LINK_PUT = 468
    NOTIFICATIONAUTOMATIONQUERYLINKS_GET = 469
    NOTIFICATIONAUTOMATIONQUERYLINKS_POST = 470
    NOTIFICATIONAUTOMATIONQUERYLINKS_LINK_PUT = 471
    NOTIFICATIONAUTOMATIONS_GET = 472
    NOTIFICATIONAUTOMATIONS_POST = 473
    NOTIFICATIONAUTOMATIONS_NOTIFICATIONAUTOMATION_PUT = 474
    NOTIFICATIONAUTOMATIONS_NOTIFICATIONAUTOMATION_STATUS_PUT = 475
    NOTIFICATIONMESSAGES_GET = 476
    NOTIFICATIONMESSAGES_POST = 477
    NOTIFICATIONMESSAGES_NOTIFICATIONMESSAGE_PUT = 478
    NOTIFICATIONS_GET = 479
    NOTIFICATIONS_POST = 480
    NOTIFICATIONS_EMPLOYEE_FILTER_POST = 481
    NOTIFICATIONS_NOTIFICATION_PUT = 482
    QUERIES_NOTIFICATIONAUTOMATION_GET = 483
    ROLENOTIFICATIONAUTOMATIONLINKS_GET = 484
    ROLENOTIFICATIONAUTOMATIONLINKS_POST = 485
    ROLENOTIFICATIONAUTOMATIONLINKS_LINK_PUT = 486
    ROLENOTIFICATIONAUTOMATIONLINKS_LINK_STATUS_PUT = 487
    EMPLOYEENOTIFICATIONAUTOMATIONLINKS_LINK_STATUS_PUT = 488
    NOTIFICATIONMESSAGES_NOTIFICATIONMESSAGE_STATUS_PUT = 489
    NOTIFICATIONAUTOMATIONQUERYLINKS_LINK_STATUS_PUT = 490
    NOTIFICATIONS_NOTIFICATIONAUTOMATION_GET = 491
    NOTIFICATIONAUTOMATIONS_NOTIFICATIONAUTOMATION_GET = 492
    NOTIFICATIONS_EMPLOYEE_VIEWED_PUT = 493
    NOTIFICATIONS_NOTIFICATION_VIEWED_PUT = 494
    NOTIFICATIONS_NOTIFICATION_STATUS_PUT = 495
    NOTIFICATIONAUTOMATIONS_EMPLOYEE_GET = 496
    NOTIFICATIONS_NOTIFICATION_ACKNOWLEDGED_PUT = 497
    CONTACTS_GET = 498
    CONTACTS_POST = 499
    CONTACTS_PUT = 500
    CONTACT_GROUPS_GET = 501
    CONTACT_GROUPS_POST = 502
    CONTACT_GROUPS_PUT = 503
    CONTACT_GROUP_CONTACT_LINKS_GET = 504
    CONTACT_GROUP_CONTACT_LINKS_POST = 505
    CONTACT_GROUP_CONTACT_LINKS_PUT = 506
    PRODUCTKITFILELINKS_PUT = 507
    UPSSHIP_POST = 508
    CARBONREPORT_GET = 509
    UPSSHIP_GET = 510
    CASEMESSAGES_POST = 511
    CASEMESSAGES_CASE_GET = 512
    CASEMESSAGES_CASE_PUT = 513
    MESSAGES_POST = 514
    MESSAGES_CASEMESSAGE_GET = 515
    MESSAGES_MESSAGE_PUT = 516
    CASEMESSAGES_FILTER_POST = 517
    SHIPPINGRECORDS_TRACKING_GET = 518
    CUSTOMERCATALOGS_GET = 519
    CASEMESSAGES_CASEID_GET = 520


class Parameters(Enum):
    # param names
    ACCOUNT = 1
    ACCOUNTID = 2
    ACCOUNTNAME = 3
    ACCOUNTURL = 4
    ACTIONID = 5
    ACTIONLINKID = 6
    ADDRESS = 7
    ADJUST_LOT = 8
    ADMINACCOUNT = 9
    ADMINPASSWORD = 10
    ALIGNER = 11
    ALIGNERID = 12
    ALIGNERID_BAGUDIDS = 13
    ALIGNERIDPATHS = 14
    ALIGNERIDS = 15
    ALIGNERIDS_BAGUDIDS = 16
    ALIGNERIDS_CASE = 17
    ALIGNERS = 18
    AMOUNT = 19
    APPLICATIONID = 20
    ASSIGNEE = 21
    ASSIGNEEIDS = 22
    ATTACHMENTID = 23
    AUXILIARY = 24
    BAGRECORDID = 25
    BAGUDID = 26
    BAKETIME = 27
    BARCODE = 28
    BASEDIR = 29
    BATCHID = 30
    BATCHIDS = 31
    BATTERY_AVG = 32
    BIN_TYPE = 33
    BINID = 34
    BODY = 35
    BRANDID = 36
    BUILDID = 37
    BULLETINID = 38
    CASE = 39
    CASEFLAGID = 40
    CASEID = 41
    CASENUMBER = 42
    CASEREPORTLINKID = 43
    CASES = 44
    CATALOG = 45
    CHANGE = 46
    CHARTID = 47
    CHARTIDS = 48
    CLEAR_LOTS = 49
    CODE = 50
    COLOR = 51
    COMPANY = 52
    CONSTANT = 53
    CONTAINER = 54
    CORRECT = 55
    COUNT = 56
    COUNTRY = 57
    CREATEDFROM = 58
    CREATEDTO = 59
    CREATEFOLDER = 60
    CUSTOMER = 61
    CUSTOMERID = 62
    CUSTOMERS = 63
    DAILYUSE = 64
    DASHBOARDID = 65
    DATE = 66
    DATEFROM = 67
    DATETO = 68
    DEFAULTVALUE = 69
    DESCRIPTION = 70
    DESTINATIONLOCATION = 71
    DIGITALSCANNER = 72
    DOCTOR = 73
    DOCTORNAME = 74
    DPMM = 75
    DUEDATE = 76
    EDATE = 77
    EMAIL = 78
    EMPID = 79
    EMPLOYEEID = 80
    EMPLOYEEIDS = 81
    ENDDATE = 82
    ENDPOINTID = 83
    ENDPOINTIDS = 84
    ENDPOINTPARAMLINKID = 85
    ENDPOINTS = 86
    EXCLUDED_LOCATIONS = 87
    EXPIRATION = 88
    EXPIREDATE = 89
    EXTENDER = 90
    FILEIDS = 91
    FILENAME = 92
    FILEPATHS = 93
    FILES = 94
    FILETYPEID = 95
    FIRSTNAME = 96
    FIXIT = 97
    FIXITID = 98
    FIXITS = 99
    FLAGID = 100
    FLAGTYPE = 101
    FLUSH = 102
    FNAME = 103
    FOLDERPATH = 104
    FOLLOWING_INSTANCE = 105
    GAUGEID = 106
    GTIN = 107
    HEXBADGE = 108
    HTMLFILE = 109
    HUMIDITY_AVG = 110
    ICON = 111
    ID = 112
    INCLUDE_FIXIT = 113
    INCLUDED_LOCATIONS = 114
    INDEX = 115
    INITIALLOCATION = 116
    INPUTS = 117
    ISDETAIL = 118
    KITID = 119
    KITS = 120
    KLPS = 121
    LABEL = 122
    LASERMARK = 123
    LASERRECORDID = 124
    LASTNAME = 125
    LATEST = 126
    LEADTIME = 127
    LEGIBLESTEP = 128
    LENGTH = 129
    LIMIT = 130
    LINEID = 131
    LINEIDS = 132
    LINK = 133
    LINKID = 134
    LINKIDS = 135
    LINKS = 136
    LINKSTOCKS = 137
    LNAME = 138
    LOCATION = 139
    LOCATIONID = 140
    LOCATIONIDS = 141
    LOCATIONS = 142
    LOCKED = 143
    LOCKID = 144
    LOCKTYPE = 145
    LOGTYPEID = 146
    LOTBATCHID = 147
    LOTID = 148
    LOTIDS = 149
    LOTNUM = 150
    LOTNUMBER = 151
    MACHINE = 152
    MACHINEID = 153
    MATERIALID = 154
    MDATE = 155
    NAME = 156
    NEW_PIN = 157
    NEWPASSWORD = 158
    NOTE = 159
    NOTES = 160
    NUMBER = 161
    OFFSET = 162
    ORDER = 163
    ORDERBY = 164
    OWNERID = 165
    OWNERIDS = 166
    PARAM = 167
    PARAMID = 168
    PARAMS = 169
    PASSWORD = 170
    PATH = 171
    PATHS = 172
    PATIENT = 173
    PATIENTFIRST = 174
    PATIENTLAST = 175
    PATTERN = 176
    PERMISSIONID = 177
    PERMISSIONIDS = 178
    PLASTICID = 179
    PLASTICTYPE = 180
    PLATE = 181
    PLATEQTY = 182
    PLATFORM_SERIAL = 183
    PREVPASSWORD = 184
    PRINTEDPARTS = 185
    PRINTSINFO = 186
    PRIORITY = 187
    PRODUCT = 188
    PRODUCTID = 189
    PRODUCTIDS = 190
    PRODUCTIONLINE = 191
    PRODUCTIONLINEID = 192
    PRODUCTS = 193
    PROFILE = 194
    QUANTITY = 195
    QUERY = 196
    QUERYCOLUMN = 197
    QUERYID = 198
    QUERYIDS = 199
    QUERYROW = 200
    QUERYSTRING = 201
    RANGE = 202
    REASON = 203
    REFERENCE = 204
    REFRESHRATE = 205
    REMOTECASENUMBER = 206
    REORDERPOINT = 207
    REPAIRTIME = 208
    REPORTID = 209
    REPORTQUERYLINKID = 210
    REPORTQUERYLINKVARIABLEID = 211
    RESETUSER = 212
    RESPONSIBLEBY = 213
    RESTRICT = 214
    ROLE = 215
    ROLEID = 216
    ROWS = 217
    RXNUMBER = 218
    SEARCHKEYWORD = 219
    SEARCHNAME = 220
    SECONDARYID = 221
    SENSOR = 222
    SERIALNUMBER = 223
    SEVERITYID = 224
    SHADE = 225
    SHADES = 226
    SHARENAME = 227
    SHEET_LENGTH_FT = 228
    SHIPADDRESS1 = 229
    SHIPADDRESS2 = 230
    SHIPCITY = 231
    SHIPCOUNTRY = 232
    SHIPDELIVERYNAME = 233
    SHIPPINGID = 234
    SHIPPINGRECORDID = 235
    SHIPSTATE = 236
    SHIPZIPCODE = 237
    SIZE = 238
    SKU = 239
    SORTORDER = 240
    SPOT_AVERAGE = 241
    SPOT_COUNT = 242
    SPOT_COVERAGE = 243
    STARTDATE = 244
    STATUS = 245
    STATUSES = 246
    STEP = 247
    STEPS = 248
    STOCKACTIONID = 249
    STOCKID = 250
    STOCKLINKID = 251
    STOCKS = 252
    STOCKSTORAGEBATCHID = 253
    STOCKSTORAGEID = 254
    STOCKTYPEID = 255
    STORAGEKEY = 256
    SUPERVISOR = 257
    TAG = 258
    TAGIDS = 259
    TAGS = 260
    TEAM = 261
    TEMP_AVG = 262
    TEST_DIAMETER = 263
    THERM_CODE = 264
    TIMEOUT_S = 265
    TITLE = 266
    TOKEN = 267
    TOKENCHECK = 268
    TOKENID = 269
    TOKENIDS = 270
    TOKENTYPE = 271
    TOTAL = 272
    TRACKING = 273
    TYPE = 274
    TYPE_STATUS = 275
    TYPEID = 276
    TYPEIDS = 277
    USERID = 278
    USERINFO = 279
    VALUE = 280
    VARIABLE = 281
    VARIABLES = 282
    VENDOR = 283
    VENDORID = 284
    VISIBILITY = 285
    WEBCOMMENTS = 286
    WEIGHT = 287
    WEIGHT_OVERRIDE = 288
    WHO = 289
    WORKORDERNOTES = 290
    YIELDID = 291
    ZPL = 292
    DICTFILES = 293
    STRTAGS = 294
    FILE = 295
    CHARTTYPEIDS = 296
    LOGTYPEIDS = 297
    STOCKIDS = 298
    CUSTOMERIDS = 299
    LOGGEDFROM = 300
    LOGGEDTO = 301
    EMPLOYEEIDSTR = 302
    STRSTEPS = 303
    PREFIX = 304
    PRACTICENAME = 305
    ADDRESS1 = 306
    ADDRESS2 = 307
    CITY = 308
    STATE = 309
    ZIPCODE = 310
    COUNTY = 311
    OFFICE_PHONE = 312
    CREATEDBY = 313
    DEAR = 314
    AVATAR = 315
    DATA = 316
    THUMBNAILLINK = 317
    UPDATE_CASE_LOCATION = 318
    UPDATE_FIXIT_LOCATION = 319
    FORGOTPASSWORD = 320
    UNIT_OF_MEASUREMENT = 321
    WASTETYPEID = 322
    TECHNICIAN = 323
    DEPARTMENT = 324
    LABNAME = 325
    MANAGER = 326
    WASTERECORDID = 327
    REMAKE = 328
    REMAKEREASON = 329
    RESETSHIPPING = 330
    FUNC = 331
    INTERVAL = 332
    NOTIFICATIONAUTOMATIONID = 333
    NOTIFICATIONMESSAGEID = 334
    MESSAGE = 335
    MESSAGEID = 336
    ACKNOWLEDGED = 337
    VIEWED = 338
    VARIABLENAME = 339
    LOGNOTE = 340
    IDS = 341
    UUID = 342
    UUIDS = 343
    LINKEMPLOYEEIDS = 344
    LINKUUID = 345
    ISVIEWED = 346
    ROLEIDS = 347
    ORDERID = 348
    CONTACTID = 349
    CONTACTGROUPID = 350
    CONTACTGROUPCONTACTLINKID = 351
    PHONENUMBER = 352
    NEWCASEID = 353
    SHIPMENT_DESCRIPTION = 354
    SHIPPER = 355
    PAYMENT_INFORMATION = 356
    SHIPTO = 357
    SHIPFROM = 358
    PACKAGE_DESCRIPTION = 359
    SERVICE = 360
    DIMENSIONS = 361
    PACKAGE_WEIGHT = 362
    PATIENTCHART = 363
    LABID = 364
    CASEMESSAGEID = 365
    CASENUMBERS = 366
    ISASC = 367


class Locations(Enum):
    # locations
    PRODUCTION = 1
    CAD_IMPORT = 2
    CAD_ALIGN = 3
    CAD_CUT = 4
    CAD_EXTRUDE = 5
    CAD_KEYJOIN = 6
    CAD_SPLINE_DRAW = 7
    CAD_SPLINE_INTERPOLATE = 8
    CAD_LASER_PLACEMENT = 9
    CAD_LASER_INTERPOLATE = 10
    UNKNOWN = 11
    CARBON = 12
    PRINTOUT = 13
    THERMO = 14
    LASER = 15
    MILL = 16
    TUMBLE = 17
    QCIN = 18
    QCOUT = 19
    BAGGING = 20
    FINALQC = 21
    GARBAGE = 22
    CAD_TEXTCUT = 23
    CREATED = 24
    COMPLETE = 25
    ROW5 = 28
    ROW6 = 29
    ROW7 = 30
    WAREHOUSE = 31
    SHELF1 = 32
    SHELF2 = 33
    CAD_EXPORT_MODEL = 34
    CAD_EXPORT_SPLINE = 35
    CAD_EXPORT_LASER = 36
    CAD_SPLINE_GENERATE = 37
    RECEIVING = 38
    INSPECT = 39
    FUSION_REPAIR = 40
    FUSION_CUT = 41
    ROW8 = 42
    PIECEWORK = 43
    PRINTIN = 44
    NC_GENERATE_COMPLETE = 45
    NC_GENERATE_FAILED = 46


class Statuses(Enum):
    # statuses
    INPROGRESS = 2
    BROKEN = 3
    COMPLETE = 4
    CANCELLED = 5
    UNAVAILABLE = 6
    AVAILABLE = 7
    INREPAIR = 8
    INLOT = 9
    TESTING = 10
    ACTIVE = 11
    INACTIVE = 12
    GOOD = 13
    BAD = 14
    UNKNOWN = 15
    MAIN = 16
    ALTER = 17
    INSTOCK = 18
    OVERSTOCK = 19
    PRODUCTION = 20
    SHELF = 21
    PUBLIC = 22
    PRIVATE = 23
    APPROVED = 24
    AWAITING_DESIGN_APPROVAL = 25
    IN_PRODUCTION = 26
    DESIGN_REJECTED = 27
    IN_DESIGN = 28
    INVOICED = 29
    INVOICED_TRYIN = 30
    ON_HOLD = 31
    ORAFIT_AWAITING_APPROVAL = 32
    OUTSOURCED = 33
    SENT_FOR_TRYIN = 34
    SUBMITTED = 35


class LogTypes(Enum):
    # logtypes
    STOCK_MOVING = 1
    STOCK_STORAGE_CREATION = 2
    ALIGNER_LOCATION_UPDATED = 3
    ALIGNER_FIXITID_UPDATED = 4
    ALIGNER_STATUS_UPDATED = 5
    ALIGNER_PRODUCT_UPDATED = 6
    ALIGNER_LOT_UPDATED = 7
    ALIGNER_CREATED = 8
    ALIGNER_REMADE = 9
    ALIGNER_FILE_LINKED = 10
    FIXIT_STATUS_UPDATED = 11
    FIXIT_CREATED = 12
    FIXIT_CHECKED_OUT = 13
    FIXIT_CANCELED = 14
    ROLL_CREATED = 15
    ROLL_STATUS_UPDATED = 16
    ROLL_LENGTH_UPDATED = 17
    ROLL_REPAIR_BEGAN = 18
    ROLL_CHECKED_OUT = 19
    YIELD_CREATED = 20
    YIELD_CHECKED_OUT = 21
    YIELD_QUANTITY_UPDATED = 22
    YIELD_STATUS_UPDATED = 23
    YIELD_REPAIR_BEGAN = 24
    YIELD_MERGED_BIN = 25
    YIELD_UNMERGED_BIN = 26
    BIN_CREATED = 27
    BIN_STATUS_UPDATED = 28
    BIN_MERGED_YIELD = 29
    BIN_UNMERGED_YIELD = 30
    LOT_CREATED = 31
    LOT_STATUS_UPDATED = 32
    LOT_CHECKED_OUT = 33
    STOCK_STATUS_UPDATED = 34
    LOCK_CREATED = 35
    LOCK_DISABLED = 36
    LOCK_EXAMINED = 37
    LOCK_READY = 38
    GAUGE_UPDATED = 39
    GAUGE_COMPLETE = 40
    GAUGE_CREATED = 41
    ALIGNER_CASE_UPDATED = 42
    STOCK_INFORMATION_UPDATED = 43
    STOCK_CREATED = 44
    STOCK_RECEIVING = 45
    LOT_BIN_UPDATED = 46
    LOT_YEILD_UPDATED = 47
    PLASTIC_BAKETIME_UPDATED = 48
    PLASTIC_UPDATED = 49
    CHECKED_IN = 50
    CHECKED_OUT = 51
    UNASSIGNED_CASE = 52
    SHIPPING_RECORD_CREATED = 53
    SHIPPING_RECORD_UPDATED = 54
    LASER_RECORD_CREATED = 55
    LASER_RECORD_UPDATED = 56
    LOT_PRODUCTION_LINE_UPDATED = 57
    BATCH_LINKED = 58
    STOCK_CHECKOUT = 59
    FIXIT_LOCATION_UPDATED = 60
    CASE_LOCATION_UPDATED = 61
