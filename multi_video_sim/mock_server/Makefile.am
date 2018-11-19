AM_CPPFLAGS = $(CXX17_FLAGS) \
	-I$(srcdir)/../util
AM_CXXFLAGS = $(PICKY_CXXFLAGS) $(EXTRA_CXXFLAGS)

bin_PROGRAMS = mock_media_server

mock_media_server_SOURCES = mock_media_server.cc
mock_media_server_LDADD = ../util/libutil.a
