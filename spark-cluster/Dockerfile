FROM openjdk:latest
RUN microdnf update
RUN microdnf install yum
ENV SPARK_VERSION 3.5.4
ENV SPARK_HOME /usr/local/share/spark
RUN curl -fL "https://downloads.apache.org/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop3.tgz" | tar xfz - -C /usr/local/share && \
    mv "/usr/local/share/spark-$SPARK_VERSION-bin-hadoop3" "$SPARK_HOME"
ENV PATH "$PATH:$SPARK_HOME/bin"
RUN yum install -y openssh-server openssh-clients hostname telnet python3
# RUN ssh-keygen -A
# COPY sshd_config /etc/ssh/sshd_config
# COPY ssh_config /etc/ssh/ssh_config
# COPY spark-env.sh /usr/local/share/spark/conf/spark-env.sh
# COPY slaves /usr/local/share/spark/conf/slaves
# RUN yum install python3-pip
CMD [ "sh", "-c", "tail -f /dev/null" ]