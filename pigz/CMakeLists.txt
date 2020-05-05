cmake_minimum_required(VERSION 3.0.2)

project(pigz C)

if(${CMAKE_C_COMPILER_ID} STREQUAL "Clang")
    # using Clang
    add_definitions(-fno-caret-diagnostics)
elseif(${CMAKE_C_COMPILER_ID} STREQUAL "GNU")
    # using GCC
    if(NOT ${CMAKE_C_COMPILER_VERSION} VERSION_LESS 4.5.0)
        add_definitions(-Wno-unused-result)
    endif()
    if(NOT ${CMAKE_C_COMPILER_VERSION} VERSION_LESS 4.8.0)
        add_definitions(-fno-diagnostics-show-caret)
    endif()
elseif(MSVC)
    # using Visual Studio
    add_definitions(-D_CRT_SECURE_NO_DEPRECATE)
endif()

set(PIGZ_SRCS
    pigz.c
    yarn.c
    try.c)

add_executable(${PROJECT_NAME} ${PIGZ_SRCS})
add_definitions(-DNOZOPFLI)

if(WIN32)
    add_definitions(-D_TIMESPEC_DEFINED)

    if(NOT DEFINED PTHREADS4W_ROOT)
        message(FATAL "Missing pthreads4w root directory")
    endif()

    set(CLEANUP_STYLE VC)
    set(PTHREADS4W_VERSION 3)

    add_subdirectory(${PTHREADS4W_ROOT} ${PTHREADS4W_ROOT} EXCLUDE_FROM_ALL)
    target_link_libraries(${PROJECT_NAME} pthreadVC3)
    target_include_directories(${PROJECT_NAME} PRIVATE win ${PTHREADS4W_ROOT})
else()
    find_package(Threads REQUIRED)
    target_link_libraries(${PROJECT_NAME} Threads::Threads)
    if(NOT APPLE)
        target_link_libraries(${PROJECT_NAME} m)
    endif()
endif()

if(NOT DEFINED ZLIB_ROOT)
    find_package(Zlib REQUIRED)
endif()

add_subdirectory(${ZLIB_ROOT} ${CMAKE_CURRENT_BINARY_DIR}/zlib EXCLUDE_FROM_ALL)

if(TARGET zlibstatic)
    set(ZLIB_TARGET zlibstatic)
else()
    set(ZLIB_TARGET zlib)
endif()

target_include_directories(${PROJECT_NAME} PRIVATE ${ZLIB_ROOT} ${CMAKE_CURRENT_BINARY_DIR}/zlib)
target_link_libraries(${PROJECT_NAME} ${ZLIB_TARGET})

if(NOT SKIP_INSTALL_BINARIES AND NOT SKIP_INSTALL_ALL)
    install(TARGETS ${PROJECT_NAME} DESTINATION "bin")
endif()