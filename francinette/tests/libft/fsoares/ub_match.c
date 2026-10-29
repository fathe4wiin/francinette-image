#include "my_utils.h"

/*
 * Part 1 must follow libc, including undefined behavior:
 *   both crash            -> match
 *   libc crashes, ft runs -> WARN (worked where a crash was expected)
 *   ft crashes, libc runs -> KO
 *   neither crashes       -> match, then compare values when the mode asks for it
 * Part 2 must not crash. A signal there is a KO.
 *
 * Libc calls go through function pointers so -Wnonnull / dead-code removal
 * cannot delete a NULL probe before it runs.
 */

int g_ub_warning = 0;

static int g_ub_case = 900;

static void enter_child(void)
{
	int fd;

	alarm(0);
	signal(SIGSEGV, SIG_DFL);
	signal(SIGABRT, SIG_DFL);
	signal(SIGBUS, SIG_DFL);
	signal(SIGILL, SIG_DFL);
	signal(SIGFPE, SIG_DFL);
	signal(SIGALRM, SIG_DFL);
	signal(SIGPIPE, SIG_DFL);
	fd = open("/dev/null", O_WRONLY);
	if (fd >= 0)
	{
		dup2(fd, STDOUT_FILENO);
		dup2(fd, STDERR_FILENO);
		if (fd > STDERR_FILENO)
			close(fd);
	}
	alarm(1);
}

static int probe(void (*fn)(void))
{
	pid_t pid;
	int status;

	pid = fork();
	if (pid < 0)
		return (-1);
	if (pid == 0)
	{
		enter_child();
		fn();
		_exit(0);
	}
	if (waitpid(pid, &status, 0) < 0)
		return (-1);
	if (WIFSIGNALED(status))
		return (WTERMSIG(status));
	if (WIFEXITED(status) && WEXITSTATUS(status) == 0)
		return (0);
	return (-1);
}

typedef struct s_int_probe
{
	int status;
	int value;
} t_int_probe;

static t_int_probe probe_int(int (*fn)(int), int arg)
{
	t_int_probe out;
	int fds[2];
	pid_t pid;
	int status;
	int value;

	out.status = -1;
	out.value = 0;
	if (pipe(fds) < 0)
		return (out);
	pid = fork();
	if (pid < 0)
	{
		close(fds[0]);
		close(fds[1]);
		return (out);
	}
	if (pid == 0)
	{
		close(fds[0]);
		enter_child();
		value = fn(arg);
		if (write(fds[1], &value, sizeof(value)) != (ssize_t)sizeof(value))
			_exit(2);
		_exit(0);
	}
	close(fds[1]);
	if (waitpid(pid, &status, 0) < 0)
	{
		close(fds[0]);
		return (out);
	}
	if (WIFSIGNALED(status))
	{
		out.status = WTERMSIG(status);
		close(fds[0]);
		return (out);
	}
	if (read(fds[0], &out.value, sizeof(out.value)) != (ssize_t)sizeof(out.value))
	{
		close(fds[0]);
		return (out);
	}
	close(fds[0]);
	out.status = 0;
	return (out);
}

static const char *sig_name(int sig)
{
	if (sig == SIGSEGV)
		return ("SIGSEGV");
	if (sig == SIGBUS)
		return ("SIGBUS");
	if (sig == SIGABRT)
		return ("SIGABRT");
	if (sig == SIGALRM)
		return ("SIGALRM");
	if (sig == SIGFPE)
		return ("SIGFPE");
	if (sig == SIGILL)
		return ("SIGILL");
	return ("a fatal signal");
}

static void warn_survived(const char *label, int sig)
{
	g_ub_warning = 1;
	if (errors_file)
		fprintf(errors_file,
			YEL "WARN" NC " %s: your function returned, libc crashed (%s).\n"
			"Expected a crash. Undefined behavior has to match libc.\n",
			label, sig_name(sig));
	printf("\n" YEL "    WARN" NC " %s: worked, but libc crashed (%s). "
		YEL "Expected a crash." NC "\n", label, sig_name(sig));
	fflush(stdout);
}

int compare_crash(const char *label, void (*std_fn)(void), void (*ft_fn)(void))
{
	int std_sig;
	int ft_sig;

	set_signature_tn(g_ub_case++, "%s", label);
	std_sig = probe(std_fn);
	ft_sig = probe(ft_fn);
	if (std_sig < 0 || ft_sig < 0)
		return (error("could not run the libc crash probe\n"));
	if (std_sig && ft_sig)
		return (1);
	if (std_sig && !ft_sig)
	{
		warn_survived(label, std_sig);
		return (1);
	}
	if (!std_sig && ft_sig)
		return (error("your function crashed (%s), libc did not\n", sig_name(ft_sig)));
	return (1);
}

int expect_no_crash(const char *label, void (*fn)(void))
{
	int sig;

	set_signature_tn(g_ub_case++, "%s", label);
	sig = probe(fn);
	if (sig < 0)
		return (error("could not run the crash guard\n"));
	if (sig)
		return (error("part 2 must not crash (%s)\n", sig_name(sig)));
	return (1);
}

static int match_one_int(const char *label, int (*std_fn)(int), int (*ft_fn)(int),
	int arg, int mode)
{
	t_int_probe stdp;
	t_int_probe ftp;
	int expected;

	set_signature_tn(g_ub_case++, "%s", label);
	stdp = probe_int(std_fn, arg);
	ftp = probe_int(ft_fn, arg);
	if (stdp.status < 0 || ftp.status < 0)
		return (error("could not run the libc comparison\n"));
	if (stdp.status && ftp.status)
		return (1);
	if (stdp.status && !ftp.status)
	{
		warn_survived(label, stdp.status);
		return (1);
	}
	if (!stdp.status && ftp.status)
		return (error("your function crashed (%s), libc did not\n", sig_name(ftp.status)));
	if (mode == UB_CRASH_ONLY)
		return (1);
	if (mode == UB_TRUTH)
	{
		expected = stdp.value ? 1 : 0;
		if (ftp.value != expected)
			return (error("expected %i (libc returned %i), yours: %i. "
				"Character checks must return 1 or 0.\n",
				expected, stdp.value, ftp.value));
		return (1);
	}
	if (ftp.value != stdp.value)
		return (error("expected %i, yours: %i\n", stdp.value, ftp.value));
	return (1);
}

int match_fn_int_extra(const char *name, int (*std_fn)(int), int (*ft_fn)(int), int mode)
{
	static const int extras[] = {
		-2, -128, -129, -255, -256, 256, 512, 1024, 4096, INT_MAX, INT_MIN
	};
	int res;
	size_t i;

	res = 1;
	for (i = 0; i < sizeof(extras) / sizeof(extras[0]); i++)
	{
		char label[80];

		snprintf(label, sizeof(label), "ft_%s(%d)", name, extras[i]);
		res = match_one_int(label, std_fn, ft_fn, extras[i], mode) && res;
		if (!res)
			break;
	}
	return (res);
}

#define SINK_SIZE(call) do { volatile size_t _sink = (size_t)(call); (void)_sink; } while (0)
#define SINK_INT(call) do { volatile int _sink = (int)(call); (void)_sink; } while (0)
#define SINK_PTR(call) do { volatile void *_sink = (void *)(call); (void)_sink; } while (0)

#ifdef CRASH_STRLEN
static size_t (*p_strlen)(const char *) = strlen;
static void std_strlen_null(void)
{
	const char *s = 0;
	SINK_SIZE(p_strlen(s));
}
static void ft_strlen_null(void)
{
	const char *s = 0;
	SINK_SIZE(ft_strlen(s));
}
int libc_crash_strlen(void)
{
	return (compare_crash("ft_strlen(NULL)", std_strlen_null, ft_strlen_null));
}
#endif

#ifdef CRASH_MEMSET
static void *(*p_memset)(void *, int, size_t) = memset;
static void std_memset_n0(void)
{
	char *s = 0;
	volatile size_t n = 0;
	SINK_PTR(p_memset(s, 0, n));
}
static void ft_memset_n0(void)
{
	char *s = 0;
	volatile size_t n = 0;
	SINK_PTR(ft_memset(s, 0, n));
}
static void std_memset_n1(void)
{
	char *s = 0;
	SINK_PTR(p_memset(s, 'a', 1));
}
static void ft_memset_n1(void)
{
	char *s = 0;
	SINK_PTR(ft_memset(s, 'a', 1));
}
int libc_crash_memset(void)
{
	int res = 1;
	res = compare_crash("ft_memset(NULL, 0, 0)", std_memset_n0, ft_memset_n0) && res;
	res = compare_crash("ft_memset(NULL, 'a', 1)", std_memset_n1, ft_memset_n1) && res;
	return (res);
}
#endif

#ifdef CRASH_BZERO
static void (*p_bzero)(void *, size_t) = bzero;
static void std_bzero_n0(void)
{
	char *s = 0;
	volatile size_t n = 0;
	p_bzero(s, n);
}
static void ft_bzero_n0(void)
{
	char *s = 0;
	volatile size_t n = 0;
	ft_bzero(s, n);
}
static void std_bzero_n1(void)
{
	char *s = 0;
	p_bzero(s, 1);
}
static void ft_bzero_n1(void)
{
	char *s = 0;
	ft_bzero(s, 1);
}
int libc_crash_bzero(void)
{
	int res = 1;
	res = compare_crash("ft_bzero(NULL, 0)", std_bzero_n0, ft_bzero_n0) && res;
	res = compare_crash("ft_bzero(NULL, 1)", std_bzero_n1, ft_bzero_n1) && res;
	return (res);
}
#endif

#ifdef CRASH_MEMCPY
static void *(*p_memcpy)(void *, const void *, size_t) = memcpy;
static void std_memcpy_n0(void)
{
	char *s = 0;
	volatile size_t n = 0;
	SINK_PTR(p_memcpy(s, s, n));
}
static void ft_memcpy_n0(void)
{
	char *s = 0;
	volatile size_t n = 0;
	SINK_PTR(ft_memcpy(s, s, n));
}
static void std_memcpy_n1(void)
{
	char *s = 0;
	SINK_PTR(p_memcpy(s, "ab", 2));
}
static void ft_memcpy_n1(void)
{
	char *s = 0;
	SINK_PTR(ft_memcpy(s, "ab", 2));
}
int libc_crash_memcpy(void)
{
	int res = 1;
	res = compare_crash("ft_memcpy(NULL, NULL, 0)", std_memcpy_n0, ft_memcpy_n0) && res;
	res = compare_crash("ft_memcpy(NULL, \"ab\", 2)", std_memcpy_n1, ft_memcpy_n1) && res;
	return (res);
}
#endif

#ifdef CRASH_MEMMOVE
static void *(*p_memmove)(void *, const void *, size_t) = memmove;
static void std_memmove_n0(void)
{
	char *s = 0;
	volatile size_t n = 0;
	SINK_PTR(p_memmove(s, s, n));
}
static void ft_memmove_n0(void)
{
	char *s = 0;
	volatile size_t n = 0;
	SINK_PTR(ft_memmove(s, s, n));
}
static void std_memmove_n1(void)
{
	char *s = 0;
	SINK_PTR(p_memmove(s, "ab", 2));
}
static void ft_memmove_n1(void)
{
	char *s = 0;
	SINK_PTR(ft_memmove(s, "ab", 2));
}
int libc_crash_memmove(void)
{
	int res = 1;
	res = compare_crash("ft_memmove(NULL, NULL, 0)", std_memmove_n0, ft_memmove_n0) && res;
	res = compare_crash("ft_memmove(NULL, \"ab\", 2)", std_memmove_n1, ft_memmove_n1) && res;
	return (res);
}
#endif

#ifdef CRASH_STRLCPY
static void std_strlcpy_both0(void)
{
	char *d = 0;
	const char *s = 0;
	volatile size_t n = 0;
	SINK_SIZE(strlcpy(d, s, n));
}
static void ft_strlcpy_both0(void)
{
	char *d = 0;
	const char *s = 0;
	volatile size_t n = 0;
	SINK_SIZE(ft_strlcpy(d, s, n));
}
static void std_strlcpy_dst(void)
{
	char *d = 0;
	SINK_SIZE(strlcpy(d, "abc", 4));
}
static void ft_strlcpy_dst(void)
{
	char *d = 0;
	SINK_SIZE(ft_strlcpy(d, "abc", 4));
}
static void std_strlcpy_src(void)
{
	char d[8] = "hi";
	const char *s = 0;
	SINK_SIZE(strlcpy(d, s, 4));
}
static void ft_strlcpy_src(void)
{
	char d[8] = "hi";
	const char *s = 0;
	SINK_SIZE(ft_strlcpy(d, s, 4));
}
int libc_crash_strlcpy(void)
{
	int res = 1;
	res = compare_crash("ft_strlcpy(NULL, NULL, 0)", std_strlcpy_both0, ft_strlcpy_both0) && res;
	res = compare_crash("ft_strlcpy(NULL, \"abc\", 4)", std_strlcpy_dst, ft_strlcpy_dst) && res;
	res = compare_crash("ft_strlcpy(dst, NULL, 4)", std_strlcpy_src, ft_strlcpy_src) && res;
	return (res);
}
#endif

#ifdef CRASH_STRLCAT
static void std_strlcat_both0(void)
{
	char *d = 0;
	const char *s = 0;
	volatile size_t n = 0;
	SINK_SIZE(strlcat(d, s, n));
}
static void ft_strlcat_both0(void)
{
	char *d = 0;
	const char *s = 0;
	volatile size_t n = 0;
	SINK_SIZE(ft_strlcat(d, s, n));
}
static void std_strlcat_dst(void)
{
	char *d = 0;
	SINK_SIZE(strlcat(d, "abc", 5));
}
static void ft_strlcat_dst(void)
{
	char *d = 0;
	SINK_SIZE(ft_strlcat(d, "abc", 5));
}
static void std_strlcat_src(void)
{
	char d[16] = "hi";
	const char *s = 0;
	SINK_SIZE(strlcat(d, s, 8));
}
static void ft_strlcat_src(void)
{
	char d[16] = "hi";
	const char *s = 0;
	SINK_SIZE(ft_strlcat(d, s, 8));
}
int libc_crash_strlcat(void)
{
	int res = 1;
	res = compare_crash("ft_strlcat(NULL, NULL, 0)", std_strlcat_both0, ft_strlcat_both0) && res;
	res = compare_crash("ft_strlcat(NULL, \"abc\", 5)", std_strlcat_dst, ft_strlcat_dst) && res;
	res = compare_crash("ft_strlcat(dst, NULL, 8)", std_strlcat_src, ft_strlcat_src) && res;
	return (res);
}
#endif

#ifdef CRASH_STRCHR
static char *(*p_strchr)(const char *, int) = strchr;
static void std_strchr_null(void)
{
	const char *s = 0;
	SINK_PTR(p_strchr(s, 'a'));
}
static void ft_strchr_null(void)
{
	const char *s = 0;
	SINK_PTR(ft_strchr(s, 'a'));
}
static void std_strchr_zero(void)
{
	const char *s = 0;
	SINK_PTR(p_strchr(s, 0));
}
static void ft_strchr_zero(void)
{
	const char *s = 0;
	SINK_PTR(ft_strchr(s, 0));
}
int libc_crash_strchr(void)
{
	int res = 1;
	res = compare_crash("ft_strchr(NULL, 'a')", std_strchr_null, ft_strchr_null) && res;
	res = compare_crash("ft_strchr(NULL, 0)", std_strchr_zero, ft_strchr_zero) && res;
	return (res);
}
#endif

#ifdef CRASH_STRRCHR
static char *(*p_strrchr)(const char *, int) = strrchr;
static void std_strrchr_null(void)
{
	const char *s = 0;
	SINK_PTR(p_strrchr(s, 'a'));
}
static void ft_strrchr_null(void)
{
	const char *s = 0;
	SINK_PTR(ft_strrchr(s, 'a'));
}
int libc_crash_strrchr(void)
{
	return (compare_crash("ft_strrchr(NULL, 'a')", std_strrchr_null, ft_strrchr_null));
}
#endif

#ifdef CRASH_STRNCMP
static int (*p_strncmp)(const char *, const char *, size_t) = strncmp;
static void std_strncmp_n0(void)
{
	const char *s = 0;
	volatile size_t n = 0;
	SINK_INT(p_strncmp(s, s, n));
}
static void ft_strncmp_n0(void)
{
	const char *s = 0;
	volatile size_t n = 0;
	SINK_INT(ft_strncmp(s, s, n));
}
static void std_strncmp_n1(void)
{
	const char *s = 0;
	SINK_INT(p_strncmp(s, "a", 1));
}
static void ft_strncmp_n1(void)
{
	const char *s = 0;
	SINK_INT(ft_strncmp(s, "a", 1));
}
static void std_strncmp_src(void)
{
	const char *s = 0;
	SINK_INT(p_strncmp("a", s, 1));
}
static void ft_strncmp_src(void)
{
	const char *s = 0;
	SINK_INT(ft_strncmp("a", s, 1));
}
int libc_crash_strncmp(void)
{
	int res = 1;
	res = compare_crash("ft_strncmp(NULL, NULL, 0)", std_strncmp_n0, ft_strncmp_n0) && res;
	res = compare_crash("ft_strncmp(NULL, \"a\", 1)", std_strncmp_n1, ft_strncmp_n1) && res;
	res = compare_crash("ft_strncmp(\"a\", NULL, 1)", std_strncmp_src, ft_strncmp_src) && res;
	return (res);
}
#endif

#ifdef CRASH_MEMCHR
static void *(*p_memchr)(const void *, int, size_t) = memchr;
static void std_memchr_n0(void)
{
	char *s = 0;
	volatile size_t n = 0;
	SINK_PTR(p_memchr(s, 'a', n));
}
static void ft_memchr_n0(void)
{
	char *s = 0;
	volatile size_t n = 0;
	SINK_PTR(ft_memchr(s, 'a', n));
}
static void std_memchr_n1(void)
{
	char *s = 0;
	SINK_PTR(p_memchr(s, 'a', 1));
}
static void ft_memchr_n1(void)
{
	char *s = 0;
	SINK_PTR(ft_memchr(s, 'a', 1));
}
int libc_crash_memchr(void)
{
	int res = 1;
	res = compare_crash("ft_memchr(NULL, 'a', 0)", std_memchr_n0, ft_memchr_n0) && res;
	res = compare_crash("ft_memchr(NULL, 'a', 1)", std_memchr_n1, ft_memchr_n1) && res;
	return (res);
}
#endif

#ifdef CRASH_MEMCMP
static int (*p_memcmp)(const void *, const void *, size_t) = memcmp;
static void std_memcmp_n0(void)
{
	char *s = 0;
	volatile size_t n = 0;
	SINK_INT(p_memcmp(s, s, n));
}
static void ft_memcmp_n0(void)
{
	char *s = 0;
	volatile size_t n = 0;
	SINK_INT(ft_memcmp(s, s, n));
}
static void std_memcmp_n1(void)
{
	char *s = 0;
	SINK_INT(p_memcmp(s, "a", 1));
}
static void ft_memcmp_n1(void)
{
	char *s = 0;
	SINK_INT(ft_memcmp(s, "a", 1));
}
int libc_crash_memcmp(void)
{
	int res = 1;
	res = compare_crash("ft_memcmp(NULL, NULL, 0)", std_memcmp_n0, ft_memcmp_n0) && res;
	res = compare_crash("ft_memcmp(NULL, \"a\", 1)", std_memcmp_n1, ft_memcmp_n1) && res;
	return (res);
}
#endif

#ifdef CRASH_STRNSTR
static void std_strnstr_n0(void)
{
	const char *s = 0;
	volatile size_t n = 0;
	SINK_PTR(strnstr(s, "a", n));
}
static void ft_strnstr_n0(void)
{
	const char *s = 0;
	volatile size_t n = 0;
	SINK_PTR(ft_strnstr(s, "a", n));
}
static void std_strnstr_n1(void)
{
	const char *s = 0;
	SINK_PTR(strnstr(s, "a", 1));
}
static void ft_strnstr_n1(void)
{
	const char *s = 0;
	SINK_PTR(ft_strnstr(s, "a", 1));
}
static void std_strnstr_needle(void)
{
	const char *s = 0;
	SINK_PTR(strnstr("abc", s, 3));
}
static void ft_strnstr_needle(void)
{
	const char *s = 0;
	SINK_PTR(ft_strnstr("abc", s, 3));
}
int libc_crash_strnstr(void)
{
	int res = 1;
	res = compare_crash("ft_strnstr(NULL, \"a\", 0)", std_strnstr_n0, ft_strnstr_n0) && res;
	res = compare_crash("ft_strnstr(NULL, \"a\", 1)", std_strnstr_n1, ft_strnstr_n1) && res;
	res = compare_crash("ft_strnstr(\"abc\", NULL, 3)", std_strnstr_needle, ft_strnstr_needle) && res;
	return (res);
}
#endif

#ifdef CRASH_ATOI
static int (*p_atoi)(const char *) = atoi;
static void std_atoi_null(void)
{
	const char *s = 0;
	SINK_INT(p_atoi(s));
}
static void ft_atoi_null(void)
{
	const char *s = 0;
	SINK_INT(ft_atoi(s));
}
int libc_crash_atoi(void)
{
	return (compare_crash("ft_atoi(NULL)", std_atoi_null, ft_atoi_null));
}
#endif

#ifdef CRASH_STRDUP
static char *(*p_strdup)(const char *) = strdup;
static void std_strdup_null(void)
{
	const char *s = 0;
	SINK_PTR(p_strdup(s));
}
static void ft_strdup_null(void)
{
	const char *s = 0;
	SINK_PTR(ft_strdup(s));
}
int libc_crash_strdup(void)
{
	return (compare_crash("ft_strdup(NULL)", std_strdup_null, ft_strdup_null));
}
#endif

#ifdef CRASH_CALLOC
typedef struct s_ptr_probe
{
	int status;
	int is_null;
} t_ptr_probe;

static t_ptr_probe probe_alloc(void *(*fn)(size_t, size_t), size_t a, size_t b)
{
	t_ptr_probe out;
	int fds[2];
	pid_t pid;
	int status;
	unsigned char flag;

	out.status = -1;
	out.is_null = 1;
	if (pipe(fds) < 0)
		return (out);
	pid = fork();
	if (pid < 0)
	{
		close(fds[0]);
		close(fds[1]);
		return (out);
	}
	if (pid == 0)
	{
		void *p;
		close(fds[0]);
		enter_child();
		p = fn(a, b);
		flag = (p == 0);
		if (write(fds[1], &flag, 1) != 1)
			_exit(2);
		_exit(0);
	}
	close(fds[1]);
	if (waitpid(pid, &status, 0) < 0)
	{
		close(fds[0]);
		return (out);
	}
	if (WIFSIGNALED(status))
	{
		out.status = WTERMSIG(status);
		close(fds[0]);
		return (out);
	}
	if (read(fds[0], &flag, 1) != 1)
	{
		close(fds[0]);
		return (out);
	}
	close(fds[0]);
	out.status = 0;
	out.is_null = flag;
	return (out);
}

int libc_crash_calloc(void)
{
	t_ptr_probe stdp;
	t_ptr_probe ftp;

	set_signature_tn(g_ub_case++, "%s", "ft_calloc((size_t)-1, (size_t)-1)");
	stdp = probe_alloc(calloc, (size_t)-1, (size_t)-1);
	ftp = probe_alloc(ft_calloc, (size_t)-1, (size_t)-1);
	if (stdp.status < 0 || ftp.status < 0)
		return (error("could not run the libc comparison\n"));
	if (stdp.status && ftp.status)
		return (1);
	if (stdp.status && !ftp.status)
	{
		warn_survived("ft_calloc((size_t)-1, (size_t)-1)", stdp.status);
		return (1);
	}
	if (!stdp.status && ftp.status)
		return (error("your function crashed (%s), libc did not\n", sig_name(ftp.status)));
	if (stdp.is_null != ftp.is_null)
		return (error("overflow result does not match libc (libc %s, yours %s)\n",
			stdp.is_null ? "NULL" : "non-NULL", ftp.is_null ? "NULL" : "non-NULL"));
	return (1);
}
#endif

#ifdef CRASH_SUBSTR
static void p2_substr_a(void)
{
	const char *s = 0;
	free(ft_substr(s, 0, 0));
}
static void p2_substr_b(void)
{
	const char *s = 0;
	free(ft_substr(s, 0, 5));
}
static void p2_substr_c(void)
{
	const char *s = 0;
	free(ft_substr(s, 3, 1));
}
int part2_guard_substr(void)
{
	int res = 1;
	res = expect_no_crash("ft_substr(NULL, 0, 0)", p2_substr_a) && res;
	res = expect_no_crash("ft_substr(NULL, 0, 5)", p2_substr_b) && res;
	res = expect_no_crash("ft_substr(NULL, 3, 1)", p2_substr_c) && res;
	return (res);
}
#endif

#ifdef CRASH_STRJOIN
static void p2_join_both(void)
{
	const char *a = 0;
	const char *b = 0;
	free(ft_strjoin(a, b));
}
static void p2_join_s1(void)
{
	const char *a = 0;
	free(ft_strjoin(a, "abc"));
}
static void p2_join_s2(void)
{
	const char *b = 0;
	free(ft_strjoin("abc", b));
}
int part2_guard_strjoin(void)
{
	int res = 1;
	res = expect_no_crash("ft_strjoin(NULL, NULL)", p2_join_both) && res;
	res = expect_no_crash("ft_strjoin(NULL, \"abc\")", p2_join_s1) && res;
	res = expect_no_crash("ft_strjoin(\"abc\", NULL)", p2_join_s2) && res;
	return (res);
}
#endif

#ifdef CRASH_STRTRIM
static void p2_trim_both(void)
{
	const char *a = 0;
	const char *b = 0;
	free(ft_strtrim(a, b));
}
static void p2_trim_s1(void)
{
	const char *a = 0;
	free(ft_strtrim(a, " ."));
}
static void p2_trim_set(void)
{
	const char *b = 0;
	free(ft_strtrim("  abc  ", b));
}
int part2_guard_strtrim(void)
{
	int res = 1;
	res = expect_no_crash("ft_strtrim(NULL, NULL)", p2_trim_both) && res;
	res = expect_no_crash("ft_strtrim(NULL, \" .\")", p2_trim_s1) && res;
	res = expect_no_crash("ft_strtrim(\"  abc  \", NULL)", p2_trim_set) && res;
	return (res);
}
#endif

#ifdef CRASH_SPLIT
static void p2_split_space(void)
{
	const char *s = 0;
	free(ft_split(s, ' '));
}
static void p2_split_zero(void)
{
	const char *s = 0;
	free(ft_split(s, '\0'));
}
int part2_guard_split(void)
{
	int res = 1;
	res = expect_no_crash("ft_split(NULL, ' ')", p2_split_space) && res;
	res = expect_no_crash("ft_split(NULL, '\\0')", p2_split_zero) && res;
	return (res);
}
#endif

#ifdef CRASH_STRMAPI
static char map_id(unsigned int i, char c)
{
	(void)i;
	return (c);
}
static void p2_mapi_null_s(void)
{
	const char *s = 0;
	free(ft_strmapi(s, map_id));
}
static void p2_mapi_null_f(void)
{
	char (*f)(unsigned int, char) = 0;
	free(ft_strmapi("abc", f));
}
int part2_guard_strmapi(void)
{
	int res = 1;
	res = expect_no_crash("ft_strmapi(NULL, f)", p2_mapi_null_s) && res;
	res = expect_no_crash("ft_strmapi(\"abc\", NULL)", p2_mapi_null_f) && res;
	return (res);
}
#endif

#ifdef CRASH_STRITERI
static void iter_id(unsigned int i, char *c)
{
	(void)i;
	(void)c;
}
static void p2_iter_null_s(void)
{
	char *s = 0;
	ft_striteri(s, iter_id);
}
static void p2_iter_null_f(void)
{
	void (*f)(unsigned int, char *) = 0;
	char buf[] = "abc";
	ft_striteri(buf, f);
}
int part2_guard_striteri(void)
{
	int res = 1;
	res = expect_no_crash("ft_striteri(NULL, f)", p2_iter_null_s) && res;
	res = expect_no_crash("ft_striteri(\"abc\", NULL)", p2_iter_null_f) && res;
	return (res);
}
#endif

#ifdef CRASH_PUTSTR_FD
static void p2_putstr_null(void)
{
	char *s = 0;
	ft_putstr_fd(s, 1);
}
static void p2_putstr_badfd(void)
{
	ft_putstr_fd("abc", -1);
}
int part2_guard_putstr_fd(void)
{
	int res = 1;
	res = expect_no_crash("ft_putstr_fd(NULL, 1)", p2_putstr_null) && res;
	res = expect_no_crash("ft_putstr_fd(\"abc\", -1)", p2_putstr_badfd) && res;
	return (res);
}
#endif

#ifdef CRASH_PUTENDL_FD
static void p2_putendl_null(void)
{
	char *s = 0;
	ft_putendl_fd(s, 1);
}
static void p2_putendl_badfd(void)
{
	ft_putendl_fd("abc", -1);
}
int part2_guard_putendl_fd(void)
{
	int res = 1;
	res = expect_no_crash("ft_putendl_fd(NULL, 1)", p2_putendl_null) && res;
	res = expect_no_crash("ft_putendl_fd(\"abc\", -1)", p2_putendl_badfd) && res;
	return (res);
}
#endif

#ifdef CRASH_PUTCHAR_FD
static void p2_putchar_badfd(void)
{
	ft_putchar_fd('a', -1);
}
int part2_guard_putchar_fd(void)
{
	return (expect_no_crash("ft_putchar_fd('a', -1)", p2_putchar_badfd));
}
#endif

#ifdef CRASH_PUTNBR_FD
static void p2_putnbr_badfd(void)
{
	ft_putnbr_fd(INT_MIN, -1);
}
int part2_guard_putnbr_fd(void)
{
	return (expect_no_crash("ft_putnbr_fd(INT_MIN, -1)", p2_putnbr_badfd));
}
#endif
