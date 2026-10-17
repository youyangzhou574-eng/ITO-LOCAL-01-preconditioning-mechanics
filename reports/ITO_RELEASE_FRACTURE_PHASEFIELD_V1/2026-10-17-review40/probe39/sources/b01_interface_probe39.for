C     OFFLINE PROBE39: manufactured interface calibration, NOT PF-CZM.
C     No SAVE, shared log, file I/O or mutable global state.
C     RECURSIVE gives invocation-local automatic working variables.
      RECURSIVE SUBROUTINE UMAT(STRESS,STATEV,DDSDDE,SSE,SPD,SCD,
     1 RPL,DDSDDT,DRPLDE,DRPLDT,STRAN,DSTRAN,TIME,DTIME,TEMP,
     2 DTEMP,PREDEF,DPRED,CMNAME,NDI,NSHR,NTENS,NSTATV,PROPS,
     3 NPROPS,COORDS,DROT,PNEWDT,CELENT,DFGRD0,DFGRD1,
     4 NOEL,NPT,LAYER,KSPT,KSTEP,KINC)
      INCLUDE 'ABA_PARAM.INC'
      CHARACTER*80 CMNAME
      DIMENSION STRESS(NTENS),STATEV(NSTATV),
     1 DDSDDE(NTENS,NTENS),DDSDDT(NTENS),DRPLDE(NTENS),
     2 STRAN(NTENS),DSTRAN(NTENS),TIME(2),PREDEF(1),DPRED(1),
     3 PROPS(NPROPS),COORDS(3),DROT(3,3),DFGRD0(3,3),
     4 DFGRD1(3,3)
      INTEGER I,J
C     Initialize every constitutive output used by this procedure.
      RPL=0.D0
      DRPLDT=0.D0
      SSE=0.D0
      SPD=0.D0
      SCD=0.D0
      DO I=1,NTENS
        STRESS(I)=0.D0
        DDSDDT(I)=0.D0
        DRPLDE(I)=0.D0
        DO J=1,NTENS
          DDSDDE(I,J)=0.D0
        ENDDO
      ENDDO
      DO I=1,NSTATV
        STATEV(I)=0.D0
      ENDDO
C     Reject ABI/model drift. This is an error path, not a solver stub.
      IF (NDI.NE.3.OR.NSHR.NE.1.OR.NTENS.NE.4) CALL XIT
      IF (NSTATV.NE.16.OR.NPROPS.NE.2) CALL XIT
      IF (PROPS(1).NE.100.D0.OR.PROPS(2).NE.0.D0) CALL XIT
      IF (NOEL.NE.101.AND.NOEL.NE.202) CALL XIT
      IF (NPT.LT.1.OR.NPT.GT.4) CALL XIT
      IF (KSTEP.LT.0.OR.KSTEP.GT.8.OR.KINC.LT.0) CALL XIT
      DO I=1,3
        DDSDDE(I,I)=PROPS(1)
      ENDDO
      DDSDDE(4,4)=PROPS(1)/2.D0
      DO I=1,NTENS
        DO J=1,NTENS
          STRESS(I)=STRESS(I)+DDSDDE(I,J)*
     1                (STRAN(J)+DSTRAN(J))
        ENDDO
        SSE=SSE+0.5D0*STRESS(I)*(STRAN(I)+DSTRAN(I))
      ENDDO
C     No temperature/history dependence; each source column is explicit.
      IF (KINC.GT.0.AND.KSTEP.GE.1.AND.KSTEP.LE.4) THEN
        IF (NPT.EQ.KSTEP) RPL=1.D0
      ENDIF
C     Solver-owned accepted-state snapshots, not a count of trial calls.
      STATEV(1)=39.D0
      STATEV(2)=DBLE(KSTEP)
      STATEV(3)=DBLE(KINC)
      STATEV(4)=DBLE(NOEL)
      STATEV(5)=DBLE(NPT)
      STATEV(6)=TEMP
      STATEV(7)=DTEMP
      STATEV(8)=TEMP+DTEMP
      STATEV(9)=COORDS(1)
      STATEV(10)=COORDS(2)
      STATEV(11)=RPL
      STATEV(12)=TIME(1)
      STATEV(13)=TIME(2)
      STATEV(14)=DTIME
      STATEV(15)=TIME(1)+DTIME
      STATEV(16)=1.D0
      RETURN
      END
