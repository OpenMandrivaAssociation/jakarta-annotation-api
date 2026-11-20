Name:		jakarta-annotation-api
Version:	3.0.0
Release:	1
Summary:	Jakarta Annotations API
Group:		Development/Java
License:	EPL-2.0 OR GPL-2.0-only WITH Classpath-exception-2.0
URL:		https://github.com/jakartaee/common-annotations-api
Source0:	https://github.com/jakartaee/common-annotations-api/archive/refs/tags/%{version}.tar.gz#/jakarta-annotation-api-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	sysjar

%description
Jakarta Annotations API 3.0.0, coordinate
jakarta.annotation:jakarta.annotation-api. The classes live in
jakarta.annotation. jakarta-annotations 1.3.5 remains the
javax.annotation jar under /usr/share/java/jakarta-annotations and
keeps the exact 1.3.5 provide that Maven, Sisu, and Gradle reference
by path. This package is the unversioned winner for the shared
coordinate.

%prep
%autosetup -n common-annotations-api-%{version} -p1
find . \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -delete
python - << 'PY'
from pathlib import Path
files = [path for path in Path("api/src/main/java").rglob("*.java") if path.name != "module-info.java"]
if len(files) != 17:
    raise SystemExit("annotation sources " + str(len(files)))
PY

%build
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
mkdir -p classes
find api/src/main/java -name '*.java' ! -name module-info.java > sources.list
test "$(wc -l < sources.list)" -eq 17
javac --release 8 -encoding UTF-8 -Xlint:-options -d classes @sources.list
jar cf jakarta.annotation-api.jar -C classes .
jar tf jakarta.annotation-api.jar | grep -E '\.(java|jar|so|node|wasm)$' && exit 1 || true
jar tf jakarta.annotation-api.jar | grep -F 'javax/annotation/' && exit 1 || true
jar tf jakarta.annotation-api.jar | grep -F module-info.class && exit 1 || true
javap -verbose -cp jakarta.annotation-api.jar jakarta.annotation.Priority | grep -F 'major version: 52'

python - << 'PY'
text = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>jakarta.annotation</groupId>
  <artifactId>jakarta.annotation-api</artifactId>
  <version>%{version}</version>
  <name>Jakarta Annotations API</name>
  <description>Jakarta Annotations API %{version}.</description>
  <url>https://github.com/jakartaee/common-annotations-api</url>
  <licenses>
    <license>
      <name>EPL-2.0 OR GPL-2.0-only WITH Classpath-exception-2.0</name>
    </license>
  </licenses>
</project>
"""
open("jakarta.annotation-api.pom", "w", encoding="utf-8").write(text)
PY

%install
sysjar install --buildroot %{buildroot} \
	--artifact jakarta.annotation-api.pom:jakarta.annotation-api.jar \
	--file-name jakarta.annotation-api \
	--filelist .mfiles

%check
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
JAR=%{buildroot}%{_javadir}/jakarta.annotation-api.jar
test -f "$JAR"
mkdir -p check
cat > check/Smoke.java << 'END'
import jakarta.annotation.Priority;
@Priority(7)
public class Smoke {
	public static void main(String[] args) {
		Priority priority = Smoke.class.getAnnotation(Priority.class);
		if (priority == null || priority.value() != 7) {
			throw new AssertionError("missing");
		}
		System.out.println("annotation_ok " + priority.value());
	}
}
END
javac --release 8 -encoding UTF-8 -Xlint:-options -cp "$JAR" -d check check/Smoke.java
java -cp "check:$JAR" Smoke > check/out.txt
cat check/out.txt
grep -F -qx 'annotation_ok 7' check/out.txt

%files -f .mfiles
%license LICENSE.md
%doc README.md NOTICE.md
